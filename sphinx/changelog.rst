#########
Changelog
#########

* `Version 1.0.7.1`_ (14.5.2019)
* `Version 1.0.7`_ (2.12.2016)
* `Version 1.0.6`_ (2.12.2016)
* `Version 1.0.5`_ (30.11.2016)
* `Version 1.0.4`_ (29.4.2016)
* `Version 1.0.3`_ (31.3.2016)

Version 1.0.7.1
===============

- Added titles of tests in analysis HTML report.

Version 1.0.7
=============

- Fixed issues with documentation.
- Added CLI option -c, --client to fbt_db utility.

Version 1.0.6
=============

- Broken release, deleted.

Version 1.0.5
=============

- New utility fbt_db for managing Firebird database with test results.

Version 1.0.4
=============

- (fbt_run) Include SKIPPED tests into results file with spec. outcome
- (fbt_run) Check that Firebird is running before test execution
- (fbt_analyze) Show time performance of tests

Version 1.0.3
=============

- (fbt_run) Allow use of custom FB client library
- (fbt_run) Return proper errorlevel (0 = all passed, 1 = otherwise)
- Allow specification of repository location. Now you can use environment variable FBT_REPO to specify directory where fbtest Repository is located.

