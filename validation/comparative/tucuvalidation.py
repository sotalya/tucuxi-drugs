#!/usr/bin/python3
import importlib.util
import platform
import sys
import time
import xml.dom.minidom

from argparse import ArgumentParser
from subprocess import Popen, CalledProcessError
from colorama import init, Fore

from sotalya.processing.tucuxirun import TucuCliRun, TucuPycliRun, TucuServerRun
from sotalya.data.query import Query

from core.utils import set_output_folder_name, get_output_folder_name
from core.systemtest import SystemTester
from core.report import Report
from core.nonmem import Nonmem
from core.extractxml import *


# globals
mgr = SystemTester()

parser = ArgumentParser(description='Tucuxi global tests comparing Tucuxi with NONMEM.',
                        prog='tucuvalidation.py')
SoftSelect = dict(both=0, only_tucuxi=1, only_nonmem=2)

# For colorama, to reset the color on every new print
init(autoreset=True)


class CrossValidator:
    """

    """

    def __init__(self, args, report: Report):
        """

        :param args:
        :param Report report:
        """
        self.args = args
        self.report = report
        self.tucuxiResult = []
        self.tucuRes = {}

    def run_query(self, query: Query, query_name: str):
        """

        :param Query query: The query to run.
        :param str query_name : Name of the query
        :return:
        """
        if self.args.whichsoft != SoftSelect['only_nonmem']:

            self.report.start_query(query.sourceFile + " : " + query.queryId)

            output_dir = os.path.join(get_output_folder_name(), 'tucuxi')

            try:
                os.makedirs(output_dir, exist_ok=True)
            except OSError as e:
                print(Fore.RED + str(e))
                self.report.jrep.add_testcase(False, 'run_query', 'run', str(e))
                return

            output_file_name = query.queryId + '.xml'
            output_file_path = os.path.join(output_dir, output_file_name)

            if self.args.tucucli != '':
                error_msg = 'No results from Tucuxi - TucuCli'

                tucuxi_run = TucuCliRun(self.args.tucucli, self.args.drugspath[0], output_file_path)
                query_response = tucuxi_run.run_tucuxi_from_file(query.sourceFile)

            elif self.args.server is not None:
                error_msg = 'No results from Tucuxi - TucuServer'

                tucuxi_run = TucuServerRun(self.args.server)
                query_response = tucuxi_run.run_tucuxi_from_file(query.sourceFile)

            else:
                error_msg = 'No results from Tucuxi - pyCli'

                tucuxi_run = TucuPycliRun(self.args.drugspath[0])
                query_response = tucuxi_run.run_tucuxi_from_file(query.sourceFile)

            if query_response is None:
                self.report.jrep.add_testcase(False, 'tucuxi_run', 'run', error_msg)
                return

            if self.args.tucucli == '':
                # Write in the output file
                xml_out = str(query_response.soup)

                # Parse xml beautifully
                xml1 = xml.dom.minidom.parseString(xml_out)
                output_string = xml1.toprettyxml(indent='    ', encoding='UTF-8')
                dom_string = os.linesep.join(
                    [s.decode('UTF-8') for s in output_string.splitlines() if s.strip()])

                with open(output_file_path, 'w', newline='') as file:
                    file.write(dom_string.replace('"', "'"))
                file.close()

            try:
                query_response_xml_extractor = QueryResponseXmlExtractor(query_response)
                responses = query_response_xml_extractor.run_extractor(query)
            except AttributeError as err:
                self.report.jrep.add_testcase(False, 'tucuxi-run', 'run', err.args[0])
                return
            except RuntimeError as err:
                self.report.jrep.add_testcase(False, 'tucuxi-run', 'run', err.args[0])
                return
            # except Exception:
            #     self.report.jrep.add_testcase(False, 'tucuxi-run', 'run', 'Unrecoverable error')
            #     return

            if not responses.responses:
                print('No results from Tucuxi!!!')
                self.report.jrep.add_testcase(False, 'tucuxi_run', 'run', error_msg)
                return

            tucuxi_response_result = []
            if True:  # args.whichsoft != SoftSelect['only_tucuxi']:
                for ri, response in enumerate(responses.responses):
                    if response.requestType == RequestType.Prediction.value:

                        if self.args.whichsoft != SoftSelect['only_tucuxi']:

                            try:

                                response.request.drugModel = mgr.drug_dict[response.request.drugModelId]
                                nm = Nonmem(query, self.args.nonmemmodelspath, response.request,
                                            mgr.drug_dict[response.request.drugModelId],
                                            response.results[0][0], not self.args.noclean, self.args.steadystate,
                                            self.args.nonmem, self.args.use_cache)

                                if hasattr(nm, 'results'):
                                    self.report.report_singlecurve(response.results, nm.results, response.request,
                                                                   query)

                                else:
                                    print('NONMEM did not succeed')
                                    self.report.jrep.add_testcase(False, 'nonmem_run', 'run', 'No results from NONMEM')
                                    self.report.report_single(response.results, response.request, query)

                            except KeyError as err:
                                print('NONMEM did not succeed')
                                self.report.jrep.add_testcase(False, 'nonmem_run', 'run', err.args[0])

                            except RuntimeError as err:
                                print('NONMEM did not succeed')
                                self.report.jrep.add_testcase(False, 'nonmem_run', 'run', err.args[0])
                                # self.report.jrep.add_testcase(False, 'nonmem_run', 'run', 'No results from NONMEM')
                                self.report.report_single(response.results, response.request, query)

                            except IndexError as err:
                                print('NONMEM did not succeed')
                                self.report.jrep.add_testcase(False, 'nonmem_run', 'run', err.args[0])
#                                self.report.jrep.add_testcase(False, 'nonmem_run', 'run', 'No results from NONMEM')
                                self.report.report_single(response.results, response.request, query)

                        else:
                            self.report.report_single(response.results, response.request, query)

                    elif response.requestType == RequestType.Adjustment.value:

                        self.report.report_adjustments(response.results, response.request, query)

                    elif response.requestType == RequestType.PredictionAtSampleTime.value:
                        if self.args.whichsoft != SoftSelect['only_tucuxi']:
                            try:
                                nm = Nonmem(query, self.args.nonmemmodelspath, response.request,
                                            mgr.drug_dict[response.request.drugModelId],
                                            response.results[0], not self.args.noclean, self.args.steadystate,
                                            self.args.nonmem, self.args.use_cache)
                                if hasattr(nm, 'results'):
                                    self.report.report_singlecurve(response.results, nm.results, response.request,
                                                                   query)
                                else:
                                    print('NONMEM did not succeed')
                                    self.report.jrep.add_testcase(False, 'nonmem_run', 'run', 'No results from NONMEM')

                            except RuntimeError as err:
                                self.report.jrep.add_testcase(False, 'nonmem_run', 'run', err.args[0])

                    elif response.requestType == RequestType.Percentiles.value:
                        if not self.args.no_percentiles:

                            # We modify the request type here
                            response.request.requestType = RequestType.Percentiles
                            try:
                                nm = Nonmem(query, self.args.nonmemmodelspath, response.request,
                                            mgr.drug_dict[response.request.drugModelId],
                                            response.results[0], not self.args.noclean, self.args.steadystate,
                                            self.args.nonmem, self.args.use_cache, self.args.nmnbpatientperthread,
                                            self.args.nmnbthreads)
                                if nm.status and hasattr(nm, 'results'):

                                    # Build the percentiles to have the same structure as Tucuxi ones
                                    r = [[], []]
                                    r[0] = nm.results[0]
                                    r[1] = []
                                    for per in range(0, len(response.request.computingTraits.computingTraits.ranks)):
                                        r[1].append([])
                                    for i in range(0, len(nm.results[1])):
                                        for percIndex in range(0,
                                                               len(response.request.computingTraits.computingTraits.
                                                                   ranks)):
                                            r[1][percIndex].append(nm.results[1][i][percIndex])

                                    self.report.report_percentiles(query, response.request, response.results, r)
                                else:
                                    # Only report Tucuxi
                                    self.report.report_single_percentiles(query, response.results, response.request)

                            except RuntimeError as err:
                                self.report.jrep.add_testcase(False, 'nonmem_run', 'run', err.args[0])

                    else:
                        self.report.jrep.add_testcase(False, 'analysis', 'run', 'Computation not compared by Python')

                    if query_name.find(".c.") != -1:
                        tucuxi_response_result.append(response.results[0][0] + response.results[0][1])

        # self.tucuxiResult.append(tucuxi_response_result.copy())
        # tucuxi_response_result.clear()
        # drug_model_id = queryName.split('.')
        # if responses.responses:
        #     print(Back.MAGENTA + '****************************************************')
        #     print(Back.MAGENTA + 'COMPARING DIFFERENT CURVES')
        #     print(Back.MAGENTA + 'Drug : {}'.format(drug_model_id[2]))
        #     print(Back.MAGENTA + 'Study : {}'.format(drug_model_id[3]))
        #     print(Back.MAGENTA + 'Covariate : {}'.format(drug_model_id[5]))
        #     print(Back.MAGENTA + '****************************************************')
        #     i = 0
        #     difference = False
        #     error = False
        #     for drugRes in self.tucuxiResult:
        #         while i + 1 <= len(drugRes):
        #             for j in range(len(drugRes)):
        #                 if j > i:
        #                     for ki, k in enumerate(drugRes[j]):
        #                         if drugRes[i][ki] != k:
        #                             difference = True
        #                             break
        #                     if not difference:
        #                         print(Fore.RED + 'Error. {req1type} with {req1ID} curve equal to {req2type} '
        #                                          'with {req2ID} curve'
        #                               .format(req1type=responses.responses[j].requestType,
        #                                       req1ID=responses.responses[j].requestId,
        #                                       req2type=responses.responses[i].requestType,
        #                                       req2ID=responses.responses[i].requestId))
        #                         error = True
        #                     difference = False
        #
        #             i += 1
        #         self.tucuxiResult.clear()
        #         if not error:
        #             print(Fore.GREEN + 'Test succeeded. All curves are different')

    def select_soft_from_args(self):
        """
        Select which software to run: tucuxi, nonmem or both. Make sure the executables are present on the machine.
        :return:
        """
        if self.args.whichsoft != SoftSelect['only_tucuxi']:
            if not os.path.isfile(self.args.nonmem):
                if self.args.use_cache:
                    print(Fore.CYAN + 'Cache mode set. All NONMEM data will be exclusively loaded from cache.')
                else:
                    try:
                        Popen(['rm -rf ' + get_output_folder_name()], shell=True)
                    except CalledProcessError as e:
                        print(Fore.RED + e.output)
                    sys.exit('Nonmem executable not found at: ' + self.args.nonmem)
        if self.args.whichsoft != SoftSelect['only_nonmem']:
            if self.args.tucucli != '':
                if not os.path.isfile(self.args.tucucli) and not os.path.isfile(self.args.tucucli + '.exe'):
                    try:
                        Popen(['rm -rf ' + get_output_folder_name()], shell=True)
                    except CalledProcessError as e:
                        print(Fore.RED + e.output)
                    sys.exit('Tucuxi cli executable not found at: ' + self.args.tucucli + '.exe or ' +
                             self.args.tucucli)
            elif self.args.server is not None:
                # ping the server
                param = '-n' if platform.system().lower() == 'windows' else '-c'

                # # Building the command. Ex: "ping -c 1 google.com"
                # command = ['ping', param, '1', self.args.server]
                # if subprocess.call(command) != 0:
                #     try:
                #         Popen(['rm -rf ' + get_output_folder_name()], shell=True)
                #     except CalledProcessError as e:
                #         print(Fore.RED + e.output)
                #     sys.exit('Tucuxi server not found or not responding. api_url: ' + self.args.server)
            else:
                # Check if the pycli module is present in the sotalya module
                if importlib.util.find_spec('.pycli', 'sotalya') is None:
                    sys.exit('Tucuxi pycli not found, check that the sotalya package installation is correct')


def parse_the_args():
    """
    * This method parses the command line arguments. This project relies on windows having unix tools
      available in the console. We get this by installing git and allowing to use it via cmd.exe.
    :return:
    """
    drugs_folder = os.path.abspath(os.path.join("..", "..", "..", "drugfiles"))
    queries_path = os.path.join("data", "queries")
    nonmem_models_path = os.path.abspath(os.path.join("data", "nonmem_models"))
    output_path = os.path.abspath('output/run_{time}'.format(time=datetime.now().strftime('%Y.%m.%d_%H.%M.%S')))
    parser.add_argument('-q', '--quiet',
                        help='Dont show all the data, kind of like release mode.', action='store_true')
    parser.add_argument('-queriespath', type=str, nargs='+', default=[queries_path],
                        help='Import folder paths for tucuxi queries (tqf)')
    parser.add_argument('-queryfile', type=str, default='', dest='query_file',
                        help='Import file path for query (tqf). If this option is set,'
                             ' then only this specific query is executed')
    parser.add_argument('-drugspath', type=str, nargs='+',
                        help='Import folder paths for Tucuxi drugfiles (tdd)',
                        default=[drugs_folder])
    parser.add_argument('-nonmemmodelspath', type=str,
                        help='Import folder paths for NonMem models',
                        default=nonmem_models_path)
    parser.add_argument('-outputpath', type=str,
                        help='Import folder paths for NonMem models',
                        default=output_path)

    parser.add_argument('-nmnbpatientperthread', type=int,
                        help='Number of patients calculated per each thread for percentiles. Default = 1000',
                        default=1000)

    parser.add_argument('-nmnbthreads', type=int,
                        help='Number of threads for NONMEM percentiles calculation. Default = 8',
                        default=8)

    # parser.add_argument('-rp', type=int,
    #                     help='Number of random generated patients per drug to be tested.', default=0)
    # parser.add_argument('-rs', type=int,
    #                     help='Number of random generated samples per random patient to be tested.', default=0)
    parser.add_argument('-d', type=str, nargs='+',
                        help='Drug IDs of drugs to be tested. (e.g. ch.heig-vd.tucuxi.imatinib)')
    parser.add_argument('-t', '--tucucli', type=str, dest='tucucli',
                        help='Command to execute Tucuxi cli, default is \'\'',
                        default='')
    parser.add_argument('-s', '--server', type=str, dest='server',
                        help='Command to execute the computation on the server, default is None',
                        nargs='?', const='http://193.134.218.125:9090/computation')
    parser.add_argument('-n', '--nonmem', type=str,
                        help='Command to execute nonmem. default = /opt/nm72/run/nmfe72',
                        default='/opt/nm72/run/nmfe72')
    parser.add_argument('-noclean',
                        help='If true will not cleanup Tucuxi afterwards.',
                        action="store_true")
    parser.add_argument('-whichsoft', type=int,
                        help='Set to run both (0), only tucuxi (1), or only nonmem (2).',
                        choices=[0, 1, 2], default=0)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('-ss', '--steadystate', type=int,
                        help='Whether or not to calculate at steady state (0 or 1),'
                             ' value of 2 will approx steady state with 10.5 cycles',
                        default=0)
    parser.add_argument('-j', '--junit', help='If set, then JUnit test reports are generated.',
                        action="store_true")
    parser.add_argument('-g', '--graph', help='If set, then graphs are generated.',
                        action="store_true")
    parser.add_argument('-cache', dest='use_cache', help='Use cache instead of calculating with NONMEM.',
                        action="store_true", default=False)
    parser.add_argument('-nopercentiles', dest='no_percentiles', help='Do not compare percentiles with NONMEM.',
                        action="store_true")
    return parser.parse_args()


def main():
    """

    :return:
    """

    args = parse_the_args()

    # pdb.set_trace()

    set_output_folder_name(os.path.abspath(args.outputpath))
    print(Fore.CYAN + get_output_folder_name())
    if not os.path.isdir(get_output_folder_name()):
        try:
            # print(Fore.CYAN + 'mkdir ' + get_foldername())
            subprocess.run('mkdir ' + get_output_folder_name(), shell=True)
        except CalledProcessError as e:
            print(Fore.RED + e.output)
            sys.exit()

    report = Report(args.graph, args.whichsoft)

    validator = CrossValidator(args, report)

    # check if necessary executables exist where we expect them
    validator.select_soft_from_args()

    # import drugs and queries
    mgr.import_drugs(args.drugspath)

    if args.query_file:
        mgr.import_query(args.query_file, args.query_file.split(os.sep)[-1])
    else:
        mgr.import_queries(args.queriespath)

    # check for conflicts in what was specified for drugs,patients,models
    # creport = mgr.check_conflicts(args.p, args.d, args.m)
    # if creport != 'none':
    #     clean_and_exit(creport)
    # print(Fore.CYAN + 'No option conflicts.')

    # generate random patients (datasets) according to the models and drugs specified
    #    mgr.generate_datasets(args.rp, args.rs, args.ss)

    #    mgr.filter_datasets(args.p, args.d, args.m)
    # mgr.filter_drugs()

    # report the situation before we run it
    mgr.print_drug()
    #    mgr.print_dataset()

#    if len(mgr.drug_dict) == 0:
#        clean_and_exit('No drugs to run, exiting.')
#    if len(mgr.query_dict) == 0:
#        clean_and_exit('No query to run, exiting.')

    for (k, v) in mgr.query_dict.items():
        set_output_folder_name(os.path.join(os.path.abspath(args.outputpath), k))
        if not os.path.isdir(get_output_folder_name()):
            try:
                print(Fore.CYAN + 'mkdir ' + get_output_folder_name())

                subprocess.run('mkdir ' + get_output_folder_name(), shell=True)
            except CalledProcessError as e:
                print(Fore.RED + e.output)
                sys.exit()

        validator.run_query(v, k)

        if args.junit:
            # The output folder has been changed for the queries. Put it back to the initial.
            set_output_folder_name(os.path.abspath(args.outputpath))
            report.write_report()

#    if not args.noclean:
#        clean()

    print(Fore.CYAN + 'End of script')

    if args.junit:
        # The output folder has been changed for the queries. Put it back to the initial.
        set_output_folder_name(os.path.abspath(args.outputpath))
        report.write_report()


if __name__ == "__main__":
    start_time = time.time()
    main()
    print(Fore.GREEN + '--- Execution time is {time} seconds ---'.format(time=(time.time() - start_time)))
