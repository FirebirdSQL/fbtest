unit fRunResult;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls, TntStdCtrls, ComCtrls, ExtCtrls;

const
  crlf = chr(13)+chr(10);
type
  TdlgResult = class(TForm)
    pnCommands: TPanel;
    btnCancel: TButton;
    btnSave: TButton;
    pgResult: TPageControl;
    tabStdOutExpected: TTabSheet;
    memoStdOutExpected: TTntMemo;
    tabStdErrExcpected: TTabSheet;
    memoStdErrExpected: TTntMemo;
    tabStdOut: TTabSheet;
    memoStdOut: TTntMemo;
    tabStdErr: TTabSheet;
    memoStdErr: TTntMemo;
    tabStdOutDiff: TTabSheet;
    tabStdErrDiff: TTabSheet;
    memoStdOutDiff: TTntMemo;
    memoStdErrDiff: TTntMemo;
    tabResult: TTabSheet;
    memoResult: TTntMemo;
    procedure btnSaveClick(Sender: TObject);
  private
    RunResult, Test, Version, Repository, _main : variant;
  public
    procedure Init(AResult, ATest, AVersion, ARepository, Main : variant);
  end;

var
  dlgResult: TdlgResult;

implementation

{$R *.dfm}

uses fMain;

procedure TdlgResult.btnSaveClick(Sender: TObject);
begin
  version.expected_stdout := memoStdOut.Lines.Text;
  version.expected_stderr := memoStdErr.Lines.Text;
  Repository.suite.save_test(Test.id);
end;

procedure TdlgResult.Init(AResult, ATest, AVersion, ARepository, Main: variant);
var
  s : string;
begin
  RunResult := AResult;
  Test := ATest;
  Version := AVersion;
  Repository := ARepository;
  _main := Main;

  pgResult.ActivePage := tabResult;

  memoResult.Lines.Clear;
  memoResult.Lines.Append('Result for '+RunResult.kind);
  memoResult.Lines.Append('ID:       '+RunResult.id);
  memoResult.Lines.Append('Version:  '+version.firebird_version);
  memoResult.Lines.Append('Platform: '+version.platform);
  memoResult.Lines.Append('');
  memoResult.Lines.Append('Outcome:  '+RunResult.outcome);
  btnSave.Enabled := RunResult.outcome = _main.Result.FAIL ;
  if Boolean(RunResult.has_key('cause')) then
    memoResult.Text := memoResult.Text + 'Cause:'+crlf
      + RunResult.GetItem('cause');
  memoResult.Lines.Append('');

  if Boolean(RunResult.has_key('failing_program')) then
    memoResult.Text := memoResult.Text + 'Failing program:'+crlf
      + FixLineEnds(RunResult.GetItem('failing_program'));
  memoResult.Lines.Append('');
  if Boolean(RunResult.has_key('db_unable_to_close')) then
    memoResult.Text := memoResult.Text + 'DB unable to close:'+crlf
      + FixLineEnds(RunResult.GetItem('db_unable_to_close'));
  memoResult.Lines.Append('');
  if Boolean(RunResult.has_key('db_unable_to_create')) then
    memoResult.Text := memoResult.Text + 'DB unable to create:'+crlf
      + FixLineEnds(RunResult.GetItem('db_unable_to_create'));
  memoResult.Lines.Append('');
  if Boolean(RunResult.has_key('db_unable_to_restore')) then
    memoResult.Text := memoResult.Text + 'DB unable to restore:'+crlf
      + FixLineEnds(RunResult.GetItem('db_unable_to_restore'));
  memoResult.Lines.Append('');
  if Boolean(RunResult.has_key('failing_script')) then
    memoResult.Text := memoResult.Text + 'Failing script:'+crlf
      + FixLineEnds(RunResult.GetItem('failing_script'));
  memoResult.Lines.Append('');

  if Boolean(RunResult.has_key('exception')) then
    memoResult.Text := memoResult.Text + 'Exception:'+crlf
      + FixLineEnds(RunResult.GetItem('exception'));
  memoResult.Lines.Append('');
  if Boolean(RunResult.has_key('traceback')) then
    memoResult.Text := memoResult.Text + 'Traceback:'+crlf
      + FixLineEnds(RunResult.GetItem('traceback'));
  memoResult.Lines.Append('');

  s := 'ISQL_stdout_expected';
  if not Boolean(RunResult.has_key(s)) then
    s := 'Python_stdout_expected';
  if Boolean(RunResult.has_key(s)) then
    memoStdOutExpected.Text := RunResult.GetItem(s);

  s := 'ISQL_stdout_actual';
  if not Boolean(RunResult.has_key(s)) then
    s := 'Python_stdout_actual';
  if Boolean(RunResult.has_key(s)) then
    memoStdOut.Text := RunResult.GetItem(s);

  s := 'ISQL_stripped_diff';
  if not Boolean(RunResult.has_key(s)) then
    s := 'Python_stripped_diff';
  if Boolean(RunResult.has_key(s)) then
    memoStdOutDiff.Text := FixLineEnds(RunResult.GetItem(s));

  s := 'ISQL_stderr_expected';
  if not Boolean(RunResult.has_key(s)) then
    s := 'Python_stderr_expected';
  if Boolean(RunResult.has_key(s)) then
    memoStdErrExpected.Text := FixLineEnds(RunResult.GetItem(s));

  s := 'ISQL_stderr_actual';
  if not Boolean(RunResult.has_key(s)) then
    s := 'Python_stderr_actual';
  if Boolean(RunResult.has_key(s)) then
    memoStdErr.Text := FixLineEnds(RunResult.GetItem(s));

  s := 'ISQL_stderr_stripped_diff';
  if not Boolean(RunResult.has_key(s)) then
    s := 'Python_stderr_stripped_diff';
  if Boolean(RunResult.has_key(s)) then
    memoStdErrDiff.Text := FixLineEnds(RunResult.GetItem(s));
end;

end.
