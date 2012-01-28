unit fRecipeEdit;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, ComCtrls, TntComCtrls, TntStdCtrls, StdCtrls, CheckLst, ExtCtrls;

type
  TfrmEditRecipe = class(TForm)
    pnTest: TPanel;
    pnCommands: TPanel;
    pgVersionDetails: TPageControl;
    tabVersion: TTabSheet;
    lblFirebirdVersion: TLabel;
    lblPlatforms: TLabel;
    lblTestType: TLabel;
    lblResources: TLabel;
    cbTestType: TComboBox;
    lbResources: TListBox;
    chklbPlatforms: TCheckListBox;
    edFirebirdVersion: TEdit;
    btnNewResource: TButton;
    btnDeleteResource: TButton;
    tabDatabase: TTabSheet;
    lblDatabase: TLabel;
    lblDatabaseName: TLabel;
    lblBackupFile: TLabel;
    lblUserName: TLabel;
    lblUserPassword: TLabel;
    lblDbCharset: TLabel;
    lblConnectionCharset: TLabel;
    lblPageSize: TLabel;
    lblDialect: TLabel;
    cbDatabase: TComboBox;
    edDatabaseName: TEdit;
    edBackupFile: TEdit;
    edUserName: TEdit;
    edUserPassword: TEdit;
    cbDbCharset: TComboBox;
    cbConnectionCharset: TComboBox;
    cbPageSize: TComboBox;
    cbDialect: TComboBox;
    tabInitScript: TTabSheet;
    memoInitScript: TTntMemo;
    TabSheet4: TTabSheet;
    memoTestScript: TTntMemo;
    tabStdOut: TTabSheet;
    memoStdOut: TTntMemo;
    tabStdErr: TTabSheet;
    memoStdErr: TTntMemo;
    tabSubstitutions: TTabSheet;
    Panel5: TPanel;
    btnNewSub: TButton;
    btnDeleteSub: TButton;
    btnReplaceSub: TButton;
    Panel7: TPanel;
    Panel6: TPanel;
    lblPattern: TLabel;
    lblReplacement: TLabel;
    edPattern: TTntEdit;
    edReplacement: TTntEdit;
    lvSubstitutions: TTntListView;
    btnCancel: TButton;
    btnSave: TButton;
    procedure btnCancelClick(Sender: TObject);
    procedure btnSaveClick(Sender: TObject);
    procedure btnNewResourceClick(Sender: TObject);
    procedure btnDeleteResourceClick(Sender: TObject);
    procedure lbResourcesClick(Sender: TObject);
    procedure lvSubstitutionsClick(Sender: TObject);
    procedure btnNewSubClick(Sender: TObject);
    procedure btnReplaceSubClick(Sender: TObject);
    procedure btnDeleteSubClick(Sender: TObject);
  private
  public
    Test, Repository, _main : variant;
    IsNew : boolean;
    Recipe: integer;
    procedure Init(ATest, ARepository, Main : variant; ARecipe: integer; AIsNew : boolean);
    function ValidateRecipe : boolean;
  end;

var
  frmEditRecipe: TfrmEditRecipe;

implementation

{$R *.dfm}

uses VarPyth, StrUtils, PythonEngine;

{ TfrmEditRecipe }

procedure TfrmEditRecipe.btnCancelClick(Sender: TObject);
begin
  // Cancel edit
end;

procedure TfrmEditRecipe.btnDeleteResourceClick(Sender: TObject);
begin
  lbResources.Items.Delete(lbResources.ItemIndex);
end;

procedure TfrmEditRecipe.btnDeleteSubClick(Sender: TObject);
begin
  lvSubstitutions.Items.Delete(lvSubstitutions.ItemIndex);
  lvSubstitutions.ItemIndex := lvSubstitutions.Items.Count - 1;
  lvSubstitutionsClick(lvSubstitutions);
end;

procedure TfrmEditRecipe.btnNewResourceClick(Sender: TObject);
var s : string;
begin
  s := InputBox('Add resource','Resource name:','');
  if Length(s) > 0 then
    lbResources.Items.Append(s);
end;

procedure TfrmEditRecipe.btnNewSubClick(Sender: TObject);
var
  li : TListItem;
begin
  li := lvSubstitutions.Items.Add ;
  li.Caption := edPattern.Text ;
  li.Data := Pointer(lvSubstitutions.Items.Count);
  li.SubItems.Add(edReplacement.Text) ;
end;

procedure TfrmEditRecipe.btnReplaceSubClick(Sender: TObject);
var
  li : TListItem;
begin
  li := lvSubstitutions.Items[lvSubstitutions.ItemIndex] ;
  li.Caption := edPattern.Text ;
  li.SubItems[0] := edReplacement.Text;
end;

procedure TfrmEditRecipe.btnSaveClick(Sender: TObject);
var
  version, substitutions, sub : Variant;
  i : integer;
  All : boolean;
  s : string;
begin
  if not ValidateRecipe then
  begin
    ModalResult := mrNone;
    exit;
  end;
  All := True;
  s := '' ;
  for i := 0 to chklbPlatforms.Items.Count - 1 do
  begin
    if not chklbPlatforms.Checked[i] then
      All := False
    else
    begin
      if Length(s) > 0 then
        s := s + ':' ;
      s := s + chklbPlatforms.Items[i] ;
    end;
  end;
  if All then s := 'All' ;

  if IsNew then
  begin
    version := _main.TestVersion(Test.id,s,edFirebirdVersion.Text,
      cbTestType.Items[cbTestType.ItemIndex],memoTestScript.Lines.Text) ;
    Test.add_version(version) ;
  end
  else
  begin
    version := Test.versions.GetItem(Recipe) ;
    version.firebird_version := edFirebirdVersion.Text;
    version.platform := s;
    version.test_type := cbTestType.Items[cbTestType.ItemIndex];
    version.test_script := memoTestScript.Lines.Text;
  end;

  version.database := cbDatabase.Items[cbDatabase.ItemIndex] ;
  if edDatabaseName.Text <> '' then
    version.database_name := edDatabaseName.Text
  else
    version.database_name := None ;
  if edBackupFile.Text <> '' then
    version.backup_file := edBackupFile.Text
  else
    version.backup_file := None ;
  if edUserName.Text <> '' then
    version.user_name := edUserName.Text
  else
    version.user_name := 'SYSDBA';
  if edUserPassword.Text <> '' then
    version.user_password := edUserPassword.Text
  else
    version.user_password := 'masterkey' ;
  if cbDbCharset.ItemIndex <> 0 then
    version.database_character_set := cbDbCharset.Items[cbDbCharset.ItemIndex]
  else
    version.database_character_set := None;
  if cbConnectionCharset.ItemIndex <> 0 then
    version.connection_character_set := cbConnectionCharset.Items[cbConnectionCharset.ItemIndex]
  else
    version.connection_character_set := None;
  if cbPageSize.ItemIndex <> 0 then
    version.page_size := cbPageSize.Items[cbPageSize.ItemIndex]
  else
    version.page_size := None;
  version.sql_dialect := StrToInt(cbDialect.Items[cbDialect.ItemIndex]);

  version.init_script := memoInitScript.Lines.Text;
  version.expected_stdout := memoStdOut.Lines.Text;
  version.expected_stderr := memoStdErr.Lines.Text;

  if lbResources.Items.Count = 0 then
    version.resources := None
  else
  begin
    version.resources := NewPythonList ;
    for i := 0 to lbResources.Items.Count - 1 do
      version.resources.append(lbResources.Items[i]) ;
  end;

  substitutions := NewPythonList;
  version.substitutions := substitutions;
  for i := 0 to lvSubstitutions.Items.Count - 1 do begin
      sub := NewPythonTuple(2) ;
      sub.SetItem(0,lvSubstitutions.Items[i].Caption);
      sub.SetItem(1,lvSubstitutions.Items[i].SubItems[0]);
      substitutions.append(sub);
  end;

  Repository.suite.save_test(Test.id);
end;

procedure TfrmEditRecipe.Init(ATest, ARepository, Main: variant; ARecipe: integer;
  AIsNew: boolean);
var
  version, substitutions, sub, pattern, replacement, v : Variant;
  i,j,k : integer;
  li : TListItem;
  s : string;
begin
  Test	:= ATest;
  Repository := ARepository;
  _main := Main ;
  IsNew := AIsNew;
  Recipe := ARecipe;
  pgVersionDetails.ActivePage := tabVersion;

  if IsNew then
  begin
    Caption := 'New Recipe for ' + Test.id ;
    memoTestScript.Lines.Text := ' ';
  end
  else
  begin
    Caption := 'Edit Recipe for ' + Test.id ;
  end;

  if Recipe >= 0 then
  begin
    version := Test.versions.GetItem(Recipe) ;
    edFirebirdVersion.Text := version.firebird_version ;
    v := version.get_platforms() ;
    for j := 0 to chklbPlatforms.Items.Count - 1 do
      chklbPlatforms.Checked[j] := False;
    for j := 0 to len(v) - 1 do
    begin
      k := chklbPlatforms.Items.IndexOf(v.GetItem(j)) ;
      chklbPlatforms.Checked[k] := (k >= 0) ;
    end;
    cbTestType.ItemIndex := cbTestType.Items.IndexOf(version.test_type) ;

    cbDatabase.ItemIndex := cbDatabase.Items.IndexOf(version.database) ;
    if version.database_name = None then
      edDatabaseName.Text := ''
    else
      edDatabaseName.Text := version.database_name ;
    if version.backup_file = None then
      edBackupFile.Text := ''
    else
      edBackupFile.Text := version.backup_file ;
    if version.user_name = 'SYSDBA' then
      edUserName.Text := ''
    else
      edUserName.Text := version.user_name ;
    if version.user_password = 'masterkey' then
      edUserPassword.Text := ''
    else
      edUserPassword.Text := version.user_password ;
    if version.database_character_set = None then
      cbDbCharset.ItemIndex := 0
    else
      cbDbCharset.ItemIndex := cbDbCharset.Items.IndexOf(version.database_character_set) ;
    if version.connection_character_set = None then
      cbConnectionCharset.ItemIndex := 0
    else
      cbConnectionCharset.ItemIndex := cbConnectionCharset.Items.IndexOf(version.connection_character_set) ;
    if version.page_size = None then
      cbPageSize.ItemIndex := 0
    else
      cbPageSize.ItemIndex := cbPageSize.Items.IndexOf(version.page_size) ;

    if VarIsPythonString(version.sql_dialect) then
      s := version.sql_dialect
    else
      s := IntToStr(version.sql_dialect);
    cbDialect.ItemIndex := cbDialect.Items.IndexOf(s) ;

    memoInitScript.Lines.Text := version.init_script;
    memoTestScript.Lines.Text := version.test_script;
    memoStdOut.Lines.Text := version.expected_stdout;
    memoStdErr.Lines.Text := version.expected_stderr;

    lbResources.Items.Clear;
    if version.resources <> None then
      for i := 0 to len(version.resources) - 1 do
        lbResources.Items.Add(version.resources.GetItem(i)) ;

    substitutions := version.substitutions;
    lvSubstitutions.Items.Clear;
    for i := 0 to len(substitutions)-1 do begin
        sub := substitutions.GetItem(i) ;
        pattern := sub.GetItem(0) ;
        replacement := sub.GetItem(1) ;
        li := lvSubstitutions.Items.Add ;
        li.Caption := pattern ;
        li.Data := Pointer(i);
        li.SubItems.Add(replacement) ;
    end;
  end
  else
  begin
    // No recipe as template
    for j := 0 to chklbPlatforms.Items.Count - 1 do
    begin
      chklbPlatforms.Checked[j] := True ;
    end;
  end

end;

procedure TfrmEditRecipe.lbResourcesClick(Sender: TObject);
begin
  btnDeleteResource.Enabled := True;
end;

procedure TfrmEditRecipe.lvSubstitutionsClick(Sender: TObject);
var item: TListItem;
begin
  if lvSubstitutions.ItemIndex < 0 then
  begin
    edPattern.Text := '' ;
    edReplacement.Text := '';
    btnDeleteSub.Enabled := False;
    btnReplaceSub.Enabled := False;
  end
  else
  begin
    item := lvSubstitutions.Items[lvSubstitutions.ItemIndex] ;
    edPattern.Text := Item.Caption ;
    if Item.SubItems.Count > 0 then
      edReplacement.Text := Item.SubItems[0]
    else
      edReplacement.Text := '';
    btnDeleteSub.Enabled := True;
    btnReplaceSub.Enabled := True;
  end;
end;

function TfrmEditRecipe.ValidateRecipe: boolean;
var
  i : integer;
  any : boolean;
begin
  result := False;
  if length(edFirebirdVersion.Text) = 0 then
  begin
    MessageDlg('Firebird version must be defined',mtError,[mbOK],0);
    exit;
  end;
  any := false;
  for i := 0 to chklbPlatforms.Items.Count - 1 do
  begin
    if chklbPlatforms.Checked[i] = True then
    begin
      any := True;
      break;
    end;
  end;
  if not any then
  begin
    MessageDlg('At least one platform must be checked',mtError,[mbOK],0);
    exit;
  end;
  if length(memoTestScript.Text) = 0 then
  begin
    MessageDlg('Test script must be defined',mtError,[mbOK],0);
    exit;
  end;
  result := True;
end;

end.
