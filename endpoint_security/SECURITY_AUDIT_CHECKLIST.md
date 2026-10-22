Tamanna AI — Endpoint Security Audit Checklist

Owner: HM INSAN ALI
Component: Endpoint Security
Version: 1.0.0
Default mode: monitor_only

1. Configuration Security

* [ ]	endpoint_config.json-এর JSON syntax যাচাই করা হয়েছে।
* [ ]	mode হলো monitor_only।
* [ ]	Process termination বন্ধ: kill_processes: false।
* [ ]	File quarantine বন্ধ: quarantine_files: false।
* [ ]	File deletion বন্ধ: delete_files: false।
* [ ]	System settings পরিবর্তন বন্ধ: modify_system_settings: false।
* [ ]	require_manual_approval সক্রিয়।
* [ ]	Command-line ও environment-variable collection বন্ধ।

Validation command:

python3 -m endpoint_security.config_validator
python3 -m endpoint_security.policy_checker

2. Unit Tests

* [ ]	Endpoint Security unit tests চালানো হয়েছে।
* [ ]	Configuration validator tests পাস করেছে।
* [ ]	Report generator tests পাস করেছে।
* [ ]	Failure ও invalid configuration cases পরীক্ষা করা হয়েছে।

Validation command:

python3 -m endpoint_security.test_runner

পরীক্ষা না চালানো পর্যন্ত কোনো item-কে সম্পন্ন হিসেবে চিহ্নিত করবে না।

3. File Integrity

* [ ]	শুধু অনুমোদিত ফাইলগুলো monitoring-এর জন্য নির্বাচন করা হয়েছে।
* [ ]	Baseline তৈরির আগে ফাইলগুলো বিশ্বস্ত কি না যাচাই করা হয়েছে।
* [ ]	Baseline file নিরাপদ স্থানে সংরক্ষিত।
* [ ]	পরিবর্তিত ফাইলের hash mismatch পরীক্ষা করা হয়েছে।
* [ ]	Missing file এবং missing baseline-এর ফল যাচাই করা হয়েছে।

Validation commands:

python3 -m endpoint_security.baseline_manager verify
python3 -m endpoint_security.integrity_scan

4. Event Logging

* [ ]	Event log-এর path সঠিক।
* [ ]	Log file-এ অনুমোদিত access control রয়েছে।
* [ ]	JSONL format যাচাই করা হয়েছে।
* [ ]	Invalid JSON records পরীক্ষা করা হয়েছে।
* [ ]	Sensitive information logging-এ প্রকাশ পাচ্ছে না তা পর্যালোচনা করা হয়েছে।
* [ ]	Log retention ও backup policy নির্ধারণ করা হয়েছে।

Validation commands:

python3 -m endpoint_security.log_validator
python3 -m endpoint_security.event_summary
python3 -m endpoint_security.event_schema_validator

5. Dependency Review

* [ ]	requirements.txt পর্যালোচনা করা হয়েছে।
* [ ]	Package versions ও compatibility যাচাই করা হয়েছে।
* [ ]	Dependencies-এর পরিচিত vulnerability আলাদা scanner দিয়ে পরীক্ষা করা হয়েছে।
* [ ]	অপ্রয়োজনীয় dependency সরানোর আগে প্রভাব পর্যালোচনা করা হয়েছে।

Validation command:

python3 -m endpoint_security.dependency_checker

এই command শুধু version declaration পরীক্ষা করে; vulnerability scan করে না।

6. GitHub Actions

* [ ]	Workflow main branch-এ সংরক্ষিত।
* [ ]	Workflow permissions contents: read।
* [ ]	GitHub Actions run সফল হয়েছে।
* [ ]	Unit test failure হলে workflow ব্যর্থ হয়।
* [ ]	কোনো production secret workflow log-এ প্রকাশ পায় না।

7. Integration Status

* [ ]	EndpointSecurityManager main server-এর সঙ্গে যুক্ত হয়েছে।
* [ ]	Monitoring কখন শুরু ও বন্ধ হয় তা নির্ধারিত।
* [ ]	Event logging বাস্তবে পরীক্ষা করা হয়েছে।
* [ ]	অনুমোদিত file paths-এর baseline যাচাই করা হয়েছে।
* [ ]	Error handling ও recovery পরীক্ষা করা হয়েছে।

গুরুত্বপূর্ণ: শুধু Python module তৈরি করলেই live endpoint protection চালু হয় না। Main server integration ও বাস্তব runtime test আলাদাভাবে যাচাই করতে হবে।

8. Final Review

* [ ]	সব test result পর্যালোচনা করা হয়েছে।
* [ ]	Open issues নথিভুক্ত করা হয়েছে।
* [ ]	Backup ও recovery পদ্ধতি যাচাই করা হয়েছে।
* [ ]	Final reviewer ও audit date নথিভুক্ত করা হয়েছে।

Audit status: Pending verification

Audit date: ____________________

Reviewer: ____________________

Notes: ____________________