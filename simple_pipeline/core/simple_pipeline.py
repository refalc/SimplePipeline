import xml.etree.ElementTree as et
import subprocess
import os
import multiprocessing
import sys
import time


class SimplePipelineRun:
    def __init__(self, exe_file=None, cmd_args=None, cd_dir=None):
        self.m_Exe = exe_file
        self.m_CmdArgs = cmd_args
        self.m_CdDir = cd_dir

    def from_element_tree(self, run_node):
        self.m_Exe = run_node.find('exe').text if run_node.find('exe') else sys.executable
        self.m_CmdArgs = run_node.find('cmd_args').text.split()
        self.m_CdDir = run_node.find('cd_dir').text if run_node.find('cd_dir') is not None else None

    def get_subprocess_args(self):
        return [self.m_Exe] + self.m_CmdArgs

    def get_cd_dir(self):
        return self.m_CdDir


class SimplePipeline:
    def __init__(self, pipeline_file, pool_processes=2):
        self.m_RunList = []
        self._from_file(pipeline_file)
        self.m_ProcessPool = multiprocessing.Pool(processes=pool_processes)

    def _from_file(self, pipeline_file):
        parsed_file = et.parse(pipeline_file)
        pipeline_root = parsed_file.getroot()
        order = 0
        for top_level_run in pipeline_root:
            if top_level_run.tag == 'run':
                current_run = SimplePipelineRun()
                current_run.from_element_tree(top_level_run)
                self.m_RunList.append((order, current_run))
                order += 1
            if top_level_run.tag == 'parallel_runs':
                parallel_run_list = []
                for parallel_run in top_level_run:
                    if parallel_run.tag == 'run':
                        current_run = SimplePipelineRun()
                        current_run.from_element_tree(parallel_run)
                        parallel_run_list.append(current_run)
                self.m_RunList.append((order, [(run, ) for run in parallel_run_list]))
                order += 1

    def run_pipeline(self, report_func=print):
        SUCCESS_CODE = 0
        for order, pipeline_run in self.m_RunList:
            if type(pipeline_run) == SimplePipelineRun:
                result_code, exec_time = self.m_ProcessPool.apply(SimplePipeline._run, args=(pipeline_run, ))
                result_status = 'OK' if result_code == SUCCESS_CODE else 'ERROR'
                report_func('exec status = {} code = {} time = {} step = {}'.format(result_status, result_code,
                                                                                    exec_time, order))
                if result_code != SUCCESS_CODE:
                    report_func('End execution with err on step {}'.format(order))
                    break
            elif type(pipeline_run) == list:
                result_info = self.m_ProcessPool.starmap(SimplePipeline._run, pipeline_run)
                result_codes = [result_code for result_code, exec_time in result_info]
                result_exec_times = [exec_time for result_code, exec_time in result_info]
                result_statuses = ['OK' if code == SUCCESS_CODE else 'ERROR' for code, exec_time in result_codes]
                report_func('exec status = {} code = {} time = {} step = {}'.format(result_statuses, result_codes,
                                                                                    result_exec_times, order))
                if result_codes.count(SUCCESS_CODE) != len(result_codes):
                    report_func('End execution with err on step {}'.format(order))

    @staticmethod
    def _run(pipeline_run):
        current_dir = os.getcwd()
        cd_dir = pipeline_run.get_cd_dir()
        if cd_dir is not None:
            os.chdir(cd_dir)

        start_time = time.time()
        res = subprocess.call(pipeline_run.get_subprocess_args())
        elapsed_time = time.time() - start_time

        if cd_dir is not None:
            os.chdir(current_dir)

        return res, elapsed_time

