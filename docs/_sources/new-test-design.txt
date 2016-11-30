=======================
How to design new tests
=======================

Where to start
==============

First, it's important to identify what you want to test. To avoid collision with others, take a look at our list of tests, and check if your beloved one is not already created! Then let us know about your intention in `firebird-test` mailing list.

If you want to create functionality tests, then you'll need Firebird SQL Reference Guide. Unfortunately, there isn't any **complete** and freely available Firebird-specific SQL reference documentation right now, but you can use `InterBase 6.0 Language Reference Guide`_ together with `Language Reference Update`_ documents.

If you want to create regression tests, please refer to `Firebird Project Tracker`_ for all bug-related informations. It's also advised to consult Firebird QA team.

The Golden Rule
===============

Test case should be really simple, and should cover only one aspect of single feature / command in discrete conditions.

Lets take the SELECT statement as an example. SELECT statement is quite complex, so you'll need to break it into clauses and choose one, for example the FIRST/SKIP. Then you need to identify all the features of that statement you want to test.

    1. SKIP only
    2. FIRST only
    3. FIRST and SKIP together

Then you can go to design test cases that would cover these features. Focus on testing all `legal paths` first (positive test) — i.e. does it work correctly as specified? If there are any behaviour-switching value boundaries, concentrate your work around them!

For example positive test cases for FIRST .. SKIP for feature "3. FIRST and SKIP together" could be defined as checking result from "select skip 10 first 5..." in next conditions:

    1. with no data — `No data` is an important condition for all DML commands
    2. with 10 rows — Behaviour-switching value boundary for SKIP
    3. with 11 rows — Behaviour-switching value boundary for SKIP and FIRST
    4. with 16 rows — Behaviour-switching value boundary for FIRST

When you have these basic test cases, you can specify various work conditions and combine these test cases with them to produce final set of test cases:

    1. Data taken from single table without WHERE predicate, i.e. table contains specified number of rows.
    2. Data taken from single table, larger resultset narrowed by WHERE predicate to specified number of rows.
    3. Data taken from joined tables, where result of this join has required number of rows.
    4. Data taken from stored procedure that generates required number of rows.
    5. SORTED result from any source of data listed above (there is no need to spawn another dimension in the matrix, as dependancy on source of data is already covered in other groups).

When legal paths are explored and covered, look at important `illegal paths` (negative tests) - does it correctly signal an error when wrong values are submitted? Because negative tests are endless, focus only on most important / expected points of failure. For example:

    1. Negative value for SKIP
    2. Negative value for FIRST

You should also define test cases for special "bizarre" values that are legal (so they do not raise an error), but are not "right" in common sense. They are used rarely, so they are often overlooked by test designers, but as they are typically behaviour-switching boundary values, their verification is very important. In case of FIRST and SKIP, this "bizarre" parameter value is zero.

Each test case has its own requirements for running environment: database schema and content, tools etc. These requirements must be a part of test case specification.

All tests have common basic structure:

    1. **Requirements** for running environment: database schema and content, tools etc.
    2. **Tested command(s)**. If test cases are well defined, then each has one and only one directly tested command. Its outcome is verified by expected output (if any), and / or with additional checks (check for right content in system tables for example).
    3. **Expected output** from tested command(s). It could be standard command output or error message. The best way to describe it is as standard ISQL output when command(s) is executed (You can use ISQL OUTPUT command to grab it). But you can define it in any other way you see fit for you and the purpose.
    4. **Additional checks**. If the direct output from tested command is not enough to verify its correctness (some commands even don't produce any "visible" output), you must use additional means (check the content in system tables, check presence of file on disk etc.)

Making test cases into tests
============================

In ideal world, each test case would be implemented as single test. This setup would provide most value for QA team, as test failure could be easily analyzed, and broken part of the engine (or in test itself) could be tracked down more precisely. Unfortunately, test implementation could require a lot of work, because each test needs its own running environment created independently from other tests. So if several test cases are closely related and use the same working environment, it could be more practical to give up on fine-grained evidence in test outcome in favour of simplified implementation, and merge them into single test.

In case of "FIRST 5 SKIP 10" we crumbled before into approx. 20 test cases we can implement some groups of test cases that use the same database and source of data in single test. For example group of test cases that take data from single table, with larger resultset narrowed by WHERE predicate to none, 10, 11 and 16 rows can easily use the same setup (database, table and table content), so we can create it 
as single test.

When you decide to wrap up several test cases into single test, keep clear what are individual test cases, i.e. don't try to make any "shortcuts" or "optimizations" in them. They should share only the common environment, nothing more. It should be also clearly stated and documented, that this paricular test contains multiple tests cases, and which they are.

From drawing board to production
================================

Once the test design is finished, it's time to implement it. If you do not want to mess up with `fbtest` and implement it yourself, you can simply write the specification for test and send it over to us.

In this case, the test specification document should contain next information:

:Test ID: Tests have hierarchical, dot-separated names / ID's, that must be unique in whole Firebird test suite. Take a look at test IDs in :ref:`Test Repository <test-repository>` for test ID examples. It would be great if test ID would conform to common schema used by Firebird QA team so it could persist, but don't worry too much about it, as it could be easily adjusted later, and the main purpose for Test ID in specification document is to have a tag that could be used to refer on test in communication between you and the QA team.
:Author:  Your name and e-mail
:Description: Clear specification what is checked by this test. If test contains more than one test case (see above), then all test cases should be described separately.
:Dependencies: Your test would very likely depend on other SQL commands, tools or Firebird features beside tested ones, so they must work correctly if the test outcome should not be spoiled. Because these features are checked by other tests, we can simply run tests in dependancy order to get unspoiled results. Of course, we could extract this information from other parts of specification, but separate list of dependencies would make the whole specification more clear and concise, and save us some time we would need to figure it out. You can simply describe these dependencies by words, or you can look up IDs for tests that must be run before this one (but it's not necessary)
:Prerequisites: Any special conditions, tools or environment required for this test (except the test database and standard tools). Most tests do not have any special requirement beyond single work database and availability of standard Firebird command-line tools, so these requirements are fulfiled automatically. But if your test needs anything else beyond that, you must enlist it here.
:Database specification: It's very likely that your test works with a database. You can give us a backup file for it (if the schema is complex or database must contain a lot of data), or you can specify how it could be created. By default, each test can get a new dialect 3 database owned by SYSDBA, with character set NONE and with page size 4K, so you don't need to specify these parameters if they are not different.If you would need this database with certain schema and populated with data, provide an ISQL script for it here. You can also refer to a database/script used in another test by test ID
:Test command(s): Self-explanatory.
:Expected result: from tested command (returned data or error code etc.)
:Additional checks: (if any) - verification from database content (for INSERT statement and the likes). DDL commands are checked against system tables. Check may query more than one table, but it's necessary to list each command and its expected output (captured output from ISQL is enough).


Example::

   Test ID: domain.alter.02
   Author: Slavomir Skopalik (skopalik at hlubocky.del.cz)

   Description:
   Checks ALTER DOMAIN...DROP DEFAULT for VARCHAR defaults

   Dependencies:

   CREATE DOMAIN
   Simple SELECT

   Prerequisites: NONE

   Database specification: Standard.
   Initialization:
   CREATE DOMAIN test VARCHAR(63) DEFAULT 'test string';

   Tested command: ALTER DOMAIN test DROP DEFAULT;
   Expected result: No stdout or stderr.

   Additional checks:
   command:
   SELECT RDB$FIELD_NAME, RDB$DEFAULT_SOURCE FROM rdb$fields WHERE RDB$FIELD_NAME = 'TEST';
   Output:
   RDB$FIELD_NAME                  RDB$DEFAULT_SOURCE
   =============================== ==================
   TEST                                          null

If you have any suggestions or criticism please drop us an e-mail in Firebird-test mailing list.


.. _Language Reference Update: http://www.firebirdsql.org/file/documentation/reference_manuals/reference_material/html/langrefupd25.html
.. _InterBase 6.0 Language Reference Guide: http://www.ibphoenix.com/files/60LangRef.zip
.. _Firebird Project Tracker: http://tracker.firebirdsql.org
