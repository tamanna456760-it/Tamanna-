#!/usr/bin/env python3
import unittest
import subprocess
import xml.etree.ElementTree as ET
import json
import tempfile
import os

class TestNmapCoreFunctionality(unittest.TestCase):
    
    def setUp(self):
        self.test_host = "scanme.nmap.org"  # Official test target
        self.local_host = "127.0.0.1"
    
    def test_nmap_installation(self):
        """Test if nmap is properly installed"""
        try:
            result = subprocess.run(['nmap', '--version'], 
                                  capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0)
            self.assertIn('Nmap version', result.stdout)
            print("✓ Nmap installation verified")
        except subprocess.TimeoutExpired:
            self.fail("Nmap version check timed out")
    
    def test_basic_scan(self):
        """Test basic TCP SYN scan"""
        try:
            cmd = ['nmap', '-sS', '-p', '22,80,443', self.test_host]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0)
            self.assertIn('Nmap scan report', result.stdout)
            print("✓ Basic SYN scan working")
        except subprocess.TimeoutExpired:
            print("⚠ Basic scan timed out (normal for external host)")
    
    def test_output_formats(self):
        """Test different output formats"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test XML output
            xml_file = os.path.join(tmpdir, 'scan.xml')
            cmd = ['nmap', '-oX', xml_file, '-p', '80', self.local_host]
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0)
            
            # Verify XML is valid
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                self.assertEqual(root.tag, 'nmaprun')
                print("✓ XML output format working")
            except ET.ParseError:
                self.fail("Invalid XML output")
            
            # Test JSON output
            json_file = os.path.join(tmpdir, 'scan.json')
            cmd = ['nmap', '-oJ', json_file, '-p', '80', self.local_host]
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0)
            
            # Verify JSON is valid
            try:
                with open(json_file, 'r') as f:
                    json_data = json.load(f)
                self.assertIsInstance(json_data, list)
                print("✓ JSON output format working")
            except json.JSONDecodeError:
                self.fail("Invalid JSON output")