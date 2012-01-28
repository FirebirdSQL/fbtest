unit fTestEdit;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls, TntStdCtrls, ExtCtrls;

type
  TfrmEditTest = class(TForm)
    pnTestHeaderFields: TPanel;
    lblTestID: TLabel;
    lblTitle: TLabel;
    lblTrackerID: TLabel;
    lblDescription: TLabel;
    edTestID: TTntEdit;
    edTitle: TTntEdit;
    edTrackerID: TTntEdit;
    memoDescription: TTntMemo;
    pnCommands: TPanel;
    btnSave: TButton;
    btnCancel: TButton;
    lblMinVersions: TLabel;
    edMinVersions: TTntEdit;
    procedure btnSaveClick(Sender: TObject);
    procedure btnCancelClick(Sender: TObject);
  private
    IsNew : boolean;
  public
    Test, Repository : variant;
    procedure Init(ATest, ARepository : variant; AIsNew : boolean);
  end;

var
  frmEditTest: TfrmEditTest;

implementation

{$R *.dfm}

uses VarPyth, StrUtils, PythonEngine;

{ TfrmEditTest }

procedure TfrmEditTest.btnCancelClick(Sender: TObject);
begin
  // Cancel edit
end;

procedure TfrmEditTest.btnSaveClick(Sender: TObject);
begin
  // Save test
  Test.title := edTitle.Text;
  Test.tracker_id := edTrackerID.Text;
  Test.min_versions := edMinVersions.Text;
  Test.description := memoDescription.Lines.Text;
  if IsNew then
    Repository.suite.add_test(Test) ; 
  Repository.suite.save_test(Test.id);
end;

procedure TfrmEditTest.Init(ATest, ARepository : variant; AIsNew : boolean);
begin
  Test	:= ATest;
  Repository := ARepository;
  IsNew := AIsNew;
  edTestID.Text := Test.id ;
  edTitle.Text := Test.title ;
  edTrackerID.Text := Test.tracker_id ;
  if Test.min_versions = None then
    edMinVersions.Text := ''
  else
    edMinVersions.Text := Test.min_versions;
  memoDescription.Lines.Text := Test.description ;
  if IsNew then
    Caption := 'New Test'
  else
    Caption := 'Edit Test '+ Test.id ;
end;

end.
