# standard libraries
import ConfigParser
import functools
import logging
import os
import sys
import time
import unittest

# local imports
from biokbase.workspace.client import Workspace
from GenomeAnnotationAPI.GenomeAnnotationAPIImpl import GenomeAnnotationAPI
from GenomeAnnotationAPI.GenomeAnnotationAPIServer import MethodContext

unittest.installHandler()

logging.basicConfig()
g_logger = logging.getLogger(__file__)
g_logger.propagate = False
log_handler = logging.StreamHandler(sys.stdout)
log_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
g_logger.addHandler(log_handler)
g_logger.setLevel(logging.INFO)

def log(func):
    if not g_logger:
        raise Exception("Missing logger for @log")

    ENTRY_MSG = "Entering {} with inputs {} {}"
    EXIT_MSG = "Exiting {}"

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        g_logger.info(ENTRY_MSG.format(func.__name__, args, kwargs))
        result = func(*args, **kwargs)
        g_logger.info(EXIT_MSG.format(func.__name__))
        return result

    return wrapper


class GenomeAnnotationAPITests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'provenance': [
                            {'service': 'GenomeAnnotationAPI',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})

        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        cls.cfg = {n[0]: n[1] for n in config.items('GenomeAnnotationAPI')}
        cls.ws = Workspace(cls.cfg['workspace-url'], token=token)
        cls.impl = GenomeAnnotationAPI(cls.cfg)

        cls.ga_ref = "8020/81/1"
        cls.genome_ref = "8020/83/1"

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.ws.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def generatePesudoRandomWorkspaceName(self):
        if hasattr(self, 'wsName'):
            return self.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_GenomeAnnotationAPI_" + str(suffix)
        ret = self.ws.create_workspace({'workspace': wsName})
        self.wsName = wsName
        return wsName

    def getType(self, ref=None):
        return self.ws.get_object_info_new({"objects": [{"ref": ref}]})[0][2]

    @log
    def test_get_taxon_old(self):
        inputs = {'ref': self.genome_ref}
        ret = self.impl.get_taxon(self.ctx, inputs)
        self.assertTrue(self.getType(ret[0]).startswith("KBaseGenomes.Genome"),
                        "ERROR: Invalid Genome reference {} from {}".format(ret[0], self.genome_ref))

    @log
    def test_get_taxon_new(self):
        inputs = {'ref': self.ga_ref}
        ret = self.impl.get_taxon(self.ctx, inputs)
        self.assertTrue(self.getType(ret[0]).startswith("KBaseGenomeAnnotations.Taxon"),
                        "ERROR: Invalid Taxon reference {} from {}".format(ret[0], self.ga_ref))

    @log
    def test_get_assembly_old(self):
        inputs = {'ref': self.genome_ref}
        ret = self.impl.get_assembly(self.ctx, inputs)
        self.assertTrue(self.getType(ret[0]).startswith("KBaseGenomes.ContigSet"),
                        "ERROR: Invalid ContigSet reference {} from {}".format(ret[0], self.genome_ref))

    @log
    def test_get_assembly_new(self):
        inputs = {'ref': self.ga_ref}
        ret = self.impl.get_assembly(self.ctx, inputs)
        self.assertTrue(self.getType(ret[0]).startswith("KBaseGenomeAnnotations.Assembly"),
                        "ERROR: Invalid Assembly reference {} from {}".format(ret[0], self.ga_ref))

    @log
    def test_get_feature_types_old(self):
        inputs = {'ref': self.genome_ref}
        ret = self.impl.get_feature_types(self.ctx, inputs)
        self.assertGreater(len(ret[0]), 0, "ERROR: No feature types present {}".format(self.genome_ref))

    @log
    def test_get_feature_types_new(self):
        inputs = {'ref': self.ga_ref}
        ret = self.impl.get_feature_types(self.ctx, inputs)
        self.assertGreater(len(ret[0]), 0, "ERROR: No feature types present {}".format(self.ga_ref))

    @log
    def test_get_feature_type_descriptions_all_old(self):
        inputs = {'ref': self.genome_ref}
        ret = self.impl.get_feature_type_descriptions(self.ctx, inputs)
        self.assertGreater(len(ret[0].keys()), 0, "ERROR: Feature type descriptions empty {}".format(self.genome_ref))

    @log
    def test_get_feature_type_descriptions_all_new(self):
        inputs = {'ref': self.ga_ref}
        ret = self.impl.get_feature_type_descriptions(self.ctx, inputs)
        self.assertGreater(len(ret[0].keys()), 0, "ERROR: Feature type descriptions empty {}".format(self.ga_ref))

    @log
    def test_get_feature_type_counts_all_old(self):
        inputs = {'ref': self.genome_ref}
        ret = self.impl.get_feature_type_counts(self.ctx, inputs)
        self.assertGreater(len(ret[0].keys()), 0, "ERROR: Feature type counts empty {}".format(self.genome_ref))

    @log
    def test_get_feature_type_counts_all_new(self):
        inputs = {'ref': self.ga_ref}
        ret = self.impl.get_feature_type_counts(self.ctx, inputs)
        self.assertGreater(len(ret[0].keys()), 0, "ERROR: Feature type counts empty {}".format(self.ga_ref))

    @log
    def test_get_feature_ids_all_old(self):
        inputs = {'ref': self.genome_ref}
        ret = self.impl.get_feature_ids(self.ctx, inputs)
        self.assertGreater(len(ret[0]), 0, "ERROR: No feature ids returned for all {}".format(self.genome_ref))

    @log
    def test_get_feature_ids_all_new(self):
        inputs = {'ref': self.ga_ref}
        ret = self.impl.get_feature_ids(self.ctx, inputs)
        self.assertGreater(len(ret[0]), 0, "ERROR: No feature ids returned for all {}".format(self.ga_ref))

    @log
    def test_get_features_all_old(self):
        inputs = {'ref': self.genome_ref}
        ret = self.impl.get_features(self.ctx, inputs)
        self.assertGreater(len(ret[0]), 0, "ERROR: No feature data returned for all {}".format(self.genome_ref))

    @log
    def test_get_features_all_exclude_sequence_false_old(self):
        inputs = {'ref': self.genome_ref, 'exclude_sequence': 0}
        ret = self.impl.get_features(self.ctx, inputs)
        self.assertGreater(len(ret[0]), 0, "ERROR: No feature data returned for all {}".format(self.genome_ref))

    @log
    def test_get_features_all_exclude_sequence_true_old(self):
        inputs = {'ref': self.genome_ref, 'exclude_sequence': 1}
        ret = self.impl.get_features(self.ctx, inputs)
        self.assertGreater(len(ret[0]), 0, "ERROR: No feature data returned for all {}".format(self.genome_ref))

    @log
    def test_get_features_all_new(self):
        inputs = {'ref': self.ga_ref}
        ret = self.impl.get_features(self.ctx, inputs)
        self.assertGreater(len(ret[0]), 0, "ERROR: No feature data returned for all {}".format(self.ga_ref))

    @log
    def test_get_features_all_exclude_sequence_false_new(self):
        inputs = {'ref': self.ga_ref, 'exclude_sequence': 0}
        ret = self.impl.get_features(self.ctx, inputs)
        self.assertGreater(len(ret[0]), 0, "ERROR: No feature data returned for all {}".format(self.ga_ref))

    @log
    def test_get_features_all_exclude_sequence_true_new(self):
        inputs = {'ref': self.ga_ref, 'exclude_sequence': 1}
        ret = self.impl.get_features(self.ctx, inputs)
        self.assertGreater(len(ret[0]), 0, "ERROR: No feature data returned for all {}".format(self.ga_ref))

    @log
    def test_get_features2_all_new(self):
        ret = self.impl.get_features2(self.ctx, {'ref':self.ga_ref, 'exclude_sequence':1})
        self.assertGreater(len(ret[0]), 0, "ERROR: No feature data returned for all {}".format(self.ga_ref))

        ret = self.impl.get_features2(self.ctx, {'ref':self.ga_ref})
        self.assertGreater(len(ret[0]), 0, "ERROR: No feature data returned for all {}".format(self.ga_ref))

        ret = self.impl.get_features2(self.ctx, {'ref':self.ga_ref, 'exclude_sequence':0})
        self.assertGreater(len(ret[0]), 0, "ERROR: No feature data returned for all {}".format(self.ga_ref))

    def test_get_proteins_all_old(self):
        inputs = {'ref': self.genome_ref}
        ret = self.impl.get_proteins(self.ctx, inputs)
        self.assertGreater(len(ret[0].keys()), 0, "ERROR: No proteins for all {}".format(self.ga_ref))

    @log
    def test_get_proteins_all_new(self):
        inputs = {'ref': self.ga_ref}
        ret = self.impl.get_proteins(self.ctx, inputs)
        self.assertGreater(len(ret[0].keys()), 0, "ERROR: No proteins for all {}".format(self.ga_ref))

    @log
    def test_get_feature_locations_all_old(self):
        inputs = {'ref': self.genome_ref}
        ret = self.impl.get_feature_locations(self.ctx, inputs)
        self.assertGreater(len(ret[0].keys()), 0, "ERROR: No locations for {}".format(self.genome_ref))

    @log
    def test_get_feature_locations_all_new(self):
        inputs = {'ref': self.ga_ref}
        ret = self.impl.get_feature_locations(self.ctx, inputs)
        self.assertGreater(len(ret[0].keys()), 0, "ERROR: No locations for {}".format(self.ga_ref))

    @log
    def test_get_feature_publications_all_old(self):
        inputs = {'ref': self.genome_ref}
        ret = self.impl.get_feature_publications(self.ctx, inputs)
        self.assertGreater(len(ret[0].keys()), 0, "ERROR: No publications for {}".format(self.genome_ref))

    @log
    def test_get_feature_publications_all_new(self):
        inputs = {'ref': self.ga_ref}
        ret = self.impl.get_feature_publications(self.ctx, inputs)
        self.assertGreater(len(ret[0].keys()), 0, "ERROR: No publications for {}".format(self.ga_ref))

    @log
    def test_get_feature_dna_all_old(self):
        inputs = {'ref': self.genome_ref}
        ret = self.impl.get_feature_dna(self.ctx, inputs)
        self.assertGreater(len(ret[0].keys()), 0, "ERROR: No DNA sequence for {}".format(self.genome_ref))

    @log
    def test_get_feature_dna_all_new(self):
        inputs = {'ref': self.ga_ref}
        ret = self.impl.get_feature_dna(self.ctx, inputs)
        self.assertGreater(len(ret[0].keys()), 0, "ERROR: No DNA sequence for {}".format(self.ga_ref))

    @log
    def test_get_feature_functions_all_old(self):
        inputs = {'ref': self.genome_ref}
        ret = self.impl.get_feature_functions(self.ctx, inputs)
        self.assertGreater(len(ret[0].keys()), 0, "ERROR: No functions for {}".format(self.genome_ref))

    @log
    def test_get_feature_functions_all_new(self):
        inputs = {'ref': self.ga_ref}
        ret = self.impl.get_feature_functions(self.ctx, inputs)
        self.assertGreater(len(ret[0].keys()), 0, "ERROR: No functions for {}".format(self.ga_ref))

    @log
    def test_get_feature_aliases_all_old(self):
        inputs = {'ref': self.genome_ref}
        ret = self.impl.get_feature_aliases(self.ctx, inputs)
        self.assertGreater(len(ret[0].keys()), 0, "ERROR: No aliases for {}".format(self.genome_ref))

    @log
    def test_get_feature_aliases_all_new(self):
        inputs = {'ref': self.ga_ref}
        ret = self.impl.get_feature_aliases(self.ctx, inputs)
        self.assertGreater(len(ret[0].keys()), 0, "ERROR: No aliases for {}".format(self.ga_ref))

    @log
    def test_get_cds_by_gene_all_old(self):
        inputs = {'ref': self.genome_ref, 'filters': {'type_list': ['gene']}, 'group_by': 'type'}
        gene_id_list = self.impl.get_feature_ids(self.ctx, inputs)[0]["by_type"]["gene"]
        inputs = {'ref': self.genome_ref, 'gene_id_list': gene_id_list}
        try:
            ret = self.impl.get_cds_by_gene(self.ctx, inputs)
            caught = False
        except TypeError:
            caught = True

        self.assertTrue(caught)

    @log
    def test_get_cds_by_gene_all_new(self):
        inputs = {'ref': self.ga_ref, 'filters': {'type_list': ['gene']}, 'group_by': 'type'}
        gene_id_list = self.impl.get_feature_ids(self.ctx, inputs)[0]["by_type"]["gene"]
        inputs = {'ref': self.ga_ref, 'gene_id_list': gene_id_list}
        ret = self.impl.get_cds_by_gene(self.ctx, inputs)
        self.assertGreater(len(ret[0].keys()), 0, "ERROR: No CDS results from gene ids {}".format(gene_id_list))

    @log
    def test_get_cds_by_mrna_all_old(self):
        inputs = {'ref': self.genome_ref, 'filters': {'type_list': ['mRNA']}, 'group_by': 'type'}
        mrna_id_list = self.impl.get_feature_ids(self.ctx, inputs)[0]["by_type"]["mRNA"]
        inputs = {'ref': self.genome_ref, 'mrna_id_list': mrna_id_list}
        try:
            ret = self.impl.get_cds_by_mrna(self.ctx, inputs)
            caught = False
        except TypeError:
            caught = True

        self.assertTrue(caught)

    @log
    def test_get_cds_by_mrna_all_new(self):
        inputs = {'ref': self.ga_ref, 'filters': {'type_list': ['mRNA']}, 'group_by': 'type'}
        mrna_id_list = self.impl.get_feature_ids(self.ctx, inputs)[0]["by_type"]["mRNA"]
        inputs = {'ref': self.ga_ref, 'mrna_id_list': mrna_id_list}
        ret = self.impl.get_cds_by_mrna(self.ctx, inputs)
        self.assertGreater(len(ret[0].keys()), 0, "ERROR: No CDS results from mRNA ids {}".format(mrna_id_list))

    @log
    def test_get_gene_by_cds_all_old(self):
        inputs = {'ref': self.genome_ref, 'filters': {'type_list': ['CDS']}, 'group_by': 'type'}
        cds_id_list = self.impl.get_feature_ids(self.ctx, inputs)[0]["by_type"]["CDS"]
        inputs = {'ref': self.genome_ref, 'cds_id_list': cds_id_list}
        try:
            ret = self.impl.get_gene_by_cds(self.ctx, inputs)
            caught = False
        except TypeError:
            caught = True

        self.assertTrue(caught)

    @log
    def test_get_gene_by_cds_all_new(self):
        inputs = {'ref': self.ga_ref, 'filters': {'type_list': ['CDS']}, 'group_by': 'type'}
        cds_id_list = self.impl.get_feature_ids(self.ctx, inputs)[0]["by_type"]["CDS"]
        inputs = {'ref': self.ga_ref, 'cds_id_list': cds_id_list}
        ret = self.impl.get_gene_by_cds(self.ctx, inputs)
        self.assertGreater(len(ret[0].keys()), 0, "ERROR: No gene results from CDS ids {}".format(cds_id_list))

    @log
    def test_get_gene_by_mrna_all_old(self):
        inputs = {'ref': self.genome_ref, 'filters': {'type_list': ['mRNA']}, 'group_by': 'type'}
        mrna_id_list = self.impl.get_feature_ids(self.ctx, inputs)[0]["by_type"]["mRNA"]
        inputs = {'ref': self.genome_ref, 'mrna_id_list': mrna_id_list}
        try:
            ret = self.impl.get_gene_by_mrna(self.ctx, inputs)
            caught = False
        except TypeError:
            caught = True

        self.assertTrue(caught)

    @log
    def test_get_gene_by_mrna_all_new(self):
        inputs = {'ref': self.ga_ref, 'filters': {'type_list': ['mRNA']}, 'group_by': 'type'}
        mrna_id_list = self.impl.get_feature_ids(self.ctx, inputs)[0]["by_type"]["mRNA"]
        inputs = {'ref': self.ga_ref, 'mrna_id_list': mrna_id_list}
        ret = self.impl.get_gene_by_mrna(self.ctx, inputs)
        self.assertGreater(len(ret[0].keys()), 0, "ERROR: No gene results from mRNA ids {}".format(mrna_id_list))

    @log
    def test_get_mrna_by_cds_all_old(self):
        inputs = {'ref': self.genome_ref, 'filters': {'type_list': ['CDS']}, 'group_by': 'type'}
        cds_id_list = self.impl.get_feature_ids(self.ctx, inputs)[0]["by_type"]["CDS"]
        inputs = {'ref': self.genome_ref, 'cds_id_list': cds_id_list}
        try:
            ret = self.impl.get_gene_by_cds(self.ctx, inputs)
            caught = False
        except TypeError:
            caught = True

        self.assertTrue(caught)

    @log
    def test_get_mrna_by_cds_all_new(self):
        inputs = {'ref': self.ga_ref, 'filters': {'type_list': ['CDS']}, 'group_by': 'type'}
        cds_id_list = self.impl.get_feature_ids(self.ctx, inputs)[0]["by_type"]["CDS"]
        inputs = {'ref': self.ga_ref, 'cds_id_list': cds_id_list}
        ret = self.impl.get_gene_by_cds(self.ctx, inputs)
        self.assertGreater(len(ret[0].keys()), 0, "ERROR: No mRNA results from cds ids {}".format(cds_id_list))

    @log
    def test_get_mrna_by_gene_all_old(self):
        inputs = {'ref': self.genome_ref, 'filters': {'type_list': ['gene']}, 'group_by': 'type'}
        gene_id_list = self.impl.get_feature_ids(self.ctx, inputs)[0]["by_type"]["gene"]
        inputs = {'ref': self.genome_ref, 'gene_id_list': gene_id_list}
        try:
            ret = self.impl.get_mrna_by_gene(self.ctx, inputs)
            caught = False
        except TypeError:
            caught = True

        self.assertTrue(caught)

    @log
    def test_get_mrna_by_gene_all_new(self):
        inputs = {'ref': self.ga_ref, 'filters': {'type_list': ['gene']}, 'group_by': 'type'}
        gene_id_list = self.impl.get_feature_ids(self.ctx, inputs)[0]["by_type"]["gene"]
        inputs = {'ref': self.ga_ref, 'gene_id_list': gene_id_list}
        ret = self.impl.get_mrna_by_gene(self.ctx, inputs)
        self.assertGreater(len(ret[0].keys()), 0, "ERROR: No mRNA results from gene ids {}".format(gene_id_list))

    @log
    def test_get_summary_old(self):
        inputs = {'ref': self.genome_ref}
        try:
            ret = self.impl.get_summary(self.ctx, inputs)
            caught = False
        except TypeError:
            caught = True

        self.assertTrue(caught)
    @log
    def test_get_summary_new(self):
        inputs = {'ref': self.ga_ref}
        ret = self.impl.get_summary(self.ctx, inputs)
        self.assertGreater(len(ret[0].keys()), 0, "ERROR: Empty summary data returned for {}".format(self.ga_ref))

    @log
    def test_get_combined_data_old(self):
        inputs = {'ref': self.genome_ref}
        ret = self.impl.get_combined_data(self.ctx, inputs)
        self.assertGreater(len(ret[0]['feature_types']), 0, "ERROR: No feature types returned for {}".format(self.ga_ref))
        self.assertGreater(len(ret[0]['feature_by_id_by_type']), 0, "ERROR: No features returned for {}".format(self.ga_ref))
        self.assertGreater(len(ret[0]['feature_by_id_by_type']['gene']), 0, "ERROR: No genes returned for {}".format(self.ga_ref))
        self.assertGreater(len(ret[0]['feature_by_id_by_type']['CDS']), 0, "ERROR: No CDSs returned for {}".format(self.ga_ref))
        self.assertGreater(len(ret[0]['protein_by_cds_id']), 0, "ERROR: No proteins returned for {}".format(self.ga_ref))
        self.assertEqual(len(ret[0]['cds_ids_by_gene_id']), 0, "ERROR: No gene-CDS links expected for {}".format(self.ga_ref))
        self.assertTrue('summary' in ret[0] and ret[0]['summary'] is not None, "ERROR: No summary returned for {}".format(self.ga_ref))

    @log
    def test_get_combined_data_new(self):
        inputs = {'ref': self.ga_ref}
        ret = self.impl.get_combined_data(self.ctx, inputs)
        self.assertGreater(len(ret[0]['feature_types']), 0, "ERROR: No feature types returned for {}".format(self.ga_ref))
        self.assertGreater(len(ret[0]['feature_by_id_by_type']), 0, "ERROR: No features returned for {}".format(self.ga_ref))
        self.assertGreater(len(ret[0]['feature_by_id_by_type']['gene']), 0, "ERROR: No genes returned for {}".format(self.ga_ref))
        self.assertGreater(len(ret[0]['feature_by_id_by_type']['CDS']), 0, "ERROR: No CDSs returned for {}".format(self.ga_ref))
        self.assertGreater(len(ret[0]['protein_by_cds_id']), 0, "ERROR: No proteins returned for {}".format(self.ga_ref))
        self.assertGreater(len(ret[0]['cds_ids_by_gene_id']), 0, "ERROR: No gene-CDS links returned for {}".format(self.ga_ref))
        self.assertTrue('summary' in ret[0] and ret[0]['summary'] is not None, "ERROR: No summary returned for {}".format(self.ga_ref))
