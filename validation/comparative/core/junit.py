#!/usr/bin/env python
# coding=utf-8

import xml.etree.cElementTree as elementTree
import xml.dom.minidom

class JUnitReport:

    def __init__(self, testsuites_name='testsuites'):
        self.suites = elementTree.Element(testsuites_name)
        self.suite = None
        self.currentSuiteName = ''

    def write_junit_report(self, filename):
        raw_xml = elementTree.tostring(self.suites, encoding='unicode')
        pretty_xml = xml.dom.minidom.parseString(raw_xml).toprettyxml(indent='  ')
        with open(filename + '.xml', 'w', encoding='utf-8') as file:
            file.write(pretty_xml)

    def add_testsuite(self, numtests):
        self.currentSuiteName = '{nt}'.format(nt=numtests)
        self.suite = elementTree.SubElement(self.suites, "testsuite", tests=self.currentSuiteName)

    def add_testcase(self, has_passed, clname, testname, failtext):
        classname = clname
        if has_passed:
            elementTree.SubElement(self.suite, "testcase", classname=classname, name=testname)
        else:
            fail = elementTree.SubElement(self.suite, "testcase", classname=classname, name=testname)
            elementTree.SubElement(fail, "failure", type="").text = failtext
