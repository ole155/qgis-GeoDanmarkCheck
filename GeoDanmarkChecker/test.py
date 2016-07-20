# coding=utf-8
import fot.featuretype
import fot.qgisapp
from fot.rules.dataset.singlelayer import UniqueAttributeValue
from fot.rules.dataset.singlelayer import AttributeRule
from fot.rules.dualdataset.compareattributes import AttributesMustNotBeChanged
from fot.rules.dualdataset.preliminaryobjects import PreliminaryObjectsRule
from fot.repository import Repository
from fot.reporter import Reporter
from fot.progress import ProgressReporter
from fot.geomutils.featurematcher import ApproximatePolygonMatcher, ApproximateLineMatcher
from fot.rules import RuleExecutor
from fot.gmlimporter import gml_to_spatialite
import os

rules = []
if True:

    # Rules applying to ALL featuretypes
    for t in fot.featuretype.featuretypes:
        rules.append(
            PreliminaryObjectsRule(
                t.name + ' preliminary objects',
                feature_type=t
            )
        )
        rules.append(
            UniqueAttributeValue(
                t.name + ' fot_id unique',
                feature_type=t,
                attributename='fot_id'
            )
        )
    # End for all t

    rules.append(
        AttributeRule(
            'Stream.vandloebstype',
            fot.featuretype.VANDLOEBSMIDTE_BRUDT,
            attributename='vandloebstype',
            isvalidfunction=lambda val: val in [u'XXAlmindelig', u'Gennem sø', u'Rørlagt']
            # validvalues=[u'XXAlmindelig', u'Gennem sø', u'Rørlagt'] #[u'Almindelig', u'Gennem sø', u'Rørlagt']
        )
    )

    rules.append(
        UniqueAttributeValue(
            'Building UUID unique',
            feature_type=fot.featuretype.BYGNING,
            attributename='bygning_id',
            filter='bygning_id IS NOT NULL'
        )
    )

    rules.append(
        AttributesMustNotBeChanged(
            'Unchanged building UUID',
            feature_type=fot.featuretype.BYGNING,
            unchangedattributes=['bygning_id'],
            featurematcher=ApproximatePolygonMatcher(relativeareadeviation=0.5),
            beforefilter='bygning_id IS NOT NULL'
        )
    )

vejmatchoptions = {'minimumintersectionlength': 1.0}  # Vi gider ikke høre om stykker kortere end 1 meter
rules.append(
    AttributesMustNotBeChanged(
        'Unchanged road attribs',
        feature_type=fot.featuretype.VEJMIDTE_BRUDT,
        unchangedattributes=[
                'kommunekode',
                'vejkode',
                'vejmyndighed',
                'vejmidtetype',
                'vejklasse_brudt',
                'trafikart_brudt',
                'overflade_brudt',
                'plads_brudt',
                'fiktiv_brudt',
                'tilogfrakoer_brudt',
                'rundkoersel_brudt'],
        featurematcher=ApproximateLineMatcher(**vejmatchoptions),
        beforefilter='vejkode IS NOT NULL'
    )
)

with fot.qgisapp.QgisStandaloneApp(True) as app:
    print "App initialised"
    # Get current dir, get parent, and join with 'testdata'
    testdata_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            os.pardir
        ),
        'testdata'
    )
    outfile = os.path.join(testdata_dir, 'output.sqlite')
    if os.path.isfile(outfile):
        os.remove(outfile)
    # gml_file = os.path.join(testdata_dir, '607_Fredericia_fot5_fra_prod.gml')
    # gml_to_spatialite(gml_file)

    reporter = Reporter(outfile)
    # reporter = ConsoleReporter('qgis')
    progress = ProgressReporter()
    before = Repository(os.path.join(testdata_dir, 'mapped_fot4.sqlite'))
    after = Repository(os.path.join(testdata_dir, 'fot5.sqlite'))
    exe = RuleExecutor(before, after)
    exe.execute(rules, reporter, progress)

    # from fot.geomutils import FeatureIndex
    # feats = after.read(fot.featuretype.BYGNING)
    # ix = FeatureIndex(feats, usespatialindex=True)
    # result = ix.geometryintersects( feats[0] )
    # print result

