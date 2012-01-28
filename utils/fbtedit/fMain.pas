unit fMain;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, PythonEngine, PythonGUIInputOutput, StdCtrls, TntStdCtrls, ExtCtrls,
  ComCtrls, JvExExtCtrls, JvExtComponent, JvItemsPanel, JvExStdCtrls,
  JvCombobox, CheckLst, TntComCtrls, ImgList, Contnrs ;

type
  TfrmMainWindow = class(TForm)
    PythonEngine1: TPythonEngine;
    PythonGUIInputOutput1: TPythonGUIInputOutput;
    OpenDialog1: TOpenDialog;
    pnCommands: TPanel;
    Panel2: TPanel;
    memoPythonOutput: TTntMemo;
    pnTest: TPanel;
    pnTreeList: TPanel;
    Splitter1: TSplitter;
    treeRepository: TTreeView;
    pnTestHeader: TPanel;
    Splitter2: TSplitter;
    memoDescription: TTntMemo;
    tabVersion: TTabSheet;
    tabDatabase: TTabSheet;
    tabInitScript: TTabSheet;
    TabSheet4: TTabSheet;
    pgVersionDetails: TPageControl;
    tabStdOut: TTabSheet;
    tabStdErr: TTabSheet;
    tabSubstitutions: TTabSheet;
    lblFirebirdVersion: TLabel;
    lblPlatforms: TLabel;
    lblTestType: TLabel;
    lblResources: TLabel;
    cbTestType: TComboBox;
    lbResources: TListBox;
    chklbPlatforms: TCheckListBox;
    edFirebirdVersion: TEdit;
    pnTestHeaderFields: TPanel;
    lblTestID: TLabel;
    edTestID: TTntEdit;
    lblTitle: TLabel;
    edTitle: TTntEdit;
    lblTrackerID: TLabel;
    edTrackerID: TTntEdit;
    lblDescription: TLabel;
    pnSeparator1: TPanel;
    btnNewTest: TButton;
    Splitter3: TSplitter;
    memoInitScript: TTntMemo;
    memoTestScript: TTntMemo;
    memoStdOut: TTntMemo;
    memoStdErr: TTntMemo;
    lblDatabase: TLabel;
    cbDatabase: TComboBox;
    lblDatabaseName: TLabel;
    edDatabaseName: TEdit;
    lblBackupFile: TLabel;
    edBackupFile: TEdit;
    lblUserName: TLabel;
    lblUserPassword: TLabel;
    edUserName: TEdit;
    edUserPassword: TEdit;
    lblDbCharset: TLabel;
    lblConnectionCharset: TLabel;
    cbDbCharset: TComboBox;
    cbConnectionCharset: TComboBox;
    lblPageSize: TLabel;
    cbPageSize: TComboBox;
    lblDialect: TLabel;
    cbDialect: TComboBox;
    Panel7: TPanel;
    lvSubstitutions: TTntListView;
    btnExecute: TButton;
    imglRepository: TImageList;
    lvRecipes: TListView;
    lblRecipes: TLabel;
    btnNewRecipe: TButton;
    btnDeleteRecipe: TButton;
    btnEditRecipe: TButton;
    gbTest: TGroupBox;
    btnEditTest: TButton;
    gbRecipe: TGroupBox;
    gbSpecial: TGroupBox;
    btnReloadTest: TButton;
    lblMinVersions: TLabel;
    edMinVersions: TTntEdit;
    procedure btnExecuteClick(Sender: TObject);
    procedure PythonEngine1SysPathInit(Sender: TObject;
      PathList: PPyObject);
    procedure FormCreate(Sender: TObject);
    procedure lvRecipesSelectItem(Sender: TObject; Item: TListItem;
      Selected: Boolean);
    procedure FormDestroy(Sender: TObject);
    procedure treeRepositoryChange(Sender: TObject; Node: TTreeNode);
    procedure btnEditTestClick(Sender: TObject);
    procedure btnEditRecipeClick(Sender: TObject);
    procedure btnNewTestClick(Sender: TObject);
    procedure btnNewRecipeClick(Sender: TObject);
    procedure btnReloadTestClick(Sender: TObject);
    procedure btnDeleteRecipeClick(Sender: TObject);
    procedure PythonEngine1PathInitialization(Sender: TObject;
      var Path: string);
    procedure PythonEngine1BeforeLoad(Sender: TObject);
  private
    _main, Repository, Runner, Test : Variant;
    script : TStrings;
    RepositoryData : TObjectList;
    Changing : boolean;
    procedure Print(s : string);
    procedure PrintList(l : variant);
    procedure PopulateTestList;
    procedure LoadTest(Id: string);
    procedure LoadRecipe(Index: integer);
    function FindNode(Items: TTreeNodes; AParent: TTreeNode; AName: string): TTreeNode; 
  public
    { Public declarations }
  end;

  TRepositoryInfoType = (riSuite, riTest);
  TRepositoryInfo = class(TObject)
    Kind : TRepositoryInfoType;
    Id : string;
    Name : string;
    constructor Create(AKind: TRepositoryInfoType;AId,AName: string);
  end;

function FixLineEnds(text: string) : string;

var
  frmMainWindow: TfrmMainWindow;


implementation

{$R *.dfm}

uses VarPyth, StrUtils, fTestEdit, fRecipeEdit,fRunResult ;

function FixLineEnds(text: string) : string;
begin
  result := ReplaceText(text,chr(10),chr(13)+chr(10));
end;

procedure TfrmMainWindow.btnDeleteRecipeClick(Sender: TObject);
var s : string;
begin
  s := 'Version: ' + lvRecipes.Items[lvRecipes.ItemIndex].Caption + chr(13)
    + 'Platforms: ' + lvRecipes.Items[lvRecipes.ItemIndex].SubItems[0] + chr(13)
    + chr(13) + 'Delete this recipe?' ;
  if MessageDlg(s,mtConfirmation,mbYesNo,0,mbNo) = mrYes then
  begin
    Test.versions.DeleteItem(lvRecipes.ItemIndex) ;
    Repository.suite.save_test(Test.id);
    LoadTest(Test.id);
  end;
end;

procedure TfrmMainWindow.btnEditRecipeClick(Sender: TObject);
var
  dlg : TfrmEditRecipe;
  Recipe : integer;
begin
  Recipe := lvRecipes.ItemIndex;
  dlg := TfrmEditRecipe.Create(self);
  try
    dlg.Init(Test,Repository,_main, Recipe,False) ;
    if dlg.ShowModal = mrOk then
    begin
      LoadTest(Test.id);
      lvRecipes.ItemIndex := Recipe;
    end;
  finally
    dlg.Free;
  end;
end;

procedure TfrmMainWindow.btnEditTestClick(Sender: TObject);
var
  dlg : TfrmEditTest;
begin
  dlg := TfrmEditTest.Create(self);
  try
    dlg.Init(Test,Repository,False) ;
    if dlg.ShowModal = mrOk then
    begin
      LoadTest(Test.id);
    end;
  finally
    dlg.Free;
  end;
end;

procedure TfrmMainWindow.btnExecuteClick(Sender: TObject);
var
  version,results,v : Variant;
  dlg : TdlgResult;
begin
  version := test.get_version_for(runner.platform,runner.version);
  v := NewPythonList;
  v.append(Test);
  results := runner.run(v);

  if results.has_key(Test.id) then
  begin
    dlg := TdlgResult.Create(self);
    try
      dlg.Init(results.GetItem(Test.id),Test,version,Repository,_main) ;
      if dlg.ShowModal = mrOk then
      begin
        LoadTest(Test.id);
        lvRecipes.ItemIndex := lvRecipes.Items.Count-1;
      end;
    finally
      dlg.Free;
    end;
  end
  else
    ShowMessage('No result returned (probably no suitable test version found)');

end;

procedure TfrmMainWindow.btnNewRecipeClick(Sender: TObject);
var
  dlg : TfrmEditRecipe;
begin
  dlg := TfrmEditRecipe.Create(self);
  try
    dlg.Init(Test,Repository,_main, lvRecipes.ItemIndex,True) ;
    if dlg.ShowModal = mrOk then
    begin
      LoadTest(Test.id);
      lvRecipes.ItemIndex := lvRecipes.Items.Count-1;
    end;
  finally
    dlg.Free;
  end;
end;

procedure TfrmMainWindow.btnNewTestClick(Sender: TObject);
var
  dlg : TfrmEditTest;
  id, s, NodeName : string;
  node, NewNode : TTreeNode;
//  i : integer;
  NewTest : variant;
  Info : TRepositoryInfo ;
begin
  // Create test.id template
  if treeRepository.Selected <> nil then
  begin
    node := treeRepository.Selected ;
    if node.ImageIndex = 0 then
      s := node.Text + '.'
    else
      s := '';
    while node.Parent <> nil do
    begin
      node := node.Parent ;
      s := node.Text + '.' + s ;
    end;
  end;
  // Ask for new test ID
  id := InputBox('New test','Test ID:',s);
  if Length(id) = 0 then
    exit;
  Test := Repository.get_test(id) ;
  if Test <> None then
  begin
    ShowMessage('Test "'+id+'" already exists!');
    exit;
  end;
  // Show edit form
  dlg := TfrmEditTest.Create(self);
  try
//    NewTest := _main.fbtest.Test(id) ;
    NewTest := _main.Test(id) ;
    dlg.Init(NewTest,Repository,True) ;
    if dlg.ShowModal = mrOk then
    begin
      Test := NewTest;
      s := id;
      node := nil;
      if pos('.',s) > 0 then
      begin
        while pos('.',s) > 0 do
        begin
          NodeName := LeftStr(s,pos('.',s)-1);
          NewNode := FindNode(treeRepository.Items,node,NodeName);
          s := RightStr(s,Length(s)-pos('.',s)) ;
          if NewNode = nil then
          begin
            Info := TRepositoryInfo.Create(riSuite,LeftStr(id,Length(id)-Length(s)-1),NodeName);
            NewNode := treeRepository.Items.AddChild(node,Info.Name) ;
            NewNode.Data := Info;
            NewNode.ImageIndex := 0;
            NewNode.SelectedIndex := 0;
          end;
          node := NewNode;
        end;
        if Length(s) > 0 then
        begin
          Info := TRepositoryInfo.Create(riTest,id,s);
          NewNode := treeRepository.Items.AddChild(node,Info.Name) ;
          NewNode.Data := Info;
          NewNode.ImageIndex := 1;
          NewNode.SelectedIndex := 1;
          node := NewNode;
        end;
      end
      else
      begin
        Info := TRepositoryInfo.Create(riTest,id,id);
        NewNode := treeRepository.Items.AddChild(node,Info.Name) ;
        NewNode.Data := Info;
        NewNode.ImageIndex := 1;
        NewNode.SelectedIndex := 1;
        node := NewNode;
      end;
      if node <> nil then
        treeRepository.Selected := node;

      //LoadTest(NewTest.id);
    end;
  finally
    dlg.Free;
  end;


end;

procedure TfrmMainWindow.btnReloadTestClick(Sender: TObject);
begin
  Repository.suite.reload_test(Test.id) ;
  LoadTest(Test.id);
end;

function TfrmMainWindow.FindNode(Items: TTreeNodes; AParent: TTreeNode;
  AName: string): TTreeNode;
var
  i : integer;
begin
  result := nil;
  for i := 0 to Items.Count - 1 do
  begin
    if (Items.Item[i].Parent = AParent) and (Items.Item[i].Text = AName) then
    begin
      result := Items.Item[i] ;
      break;
    end;
  end;
end;

procedure TfrmMainWindow.FormCreate(Sender: TObject);
begin
  Changing := False;
  RepositoryData := TObjectList.Create ;
  script := TStringList.Create ;
  script.LoadFromFile('fbtest_init.py');
{
  script.Add('import os') ;
  script.Add('import fbtest') ;
  script.Add('repository = fbtest.Repository(os.getcwd())') ;
  script.Add('repository.load()') ;
  script.Add('runner = fbtest.Runner(repository)') ;
  script.Add('runner.set_target("XX","localhost")') ;
}
  PythonEngine1.ExecStrings(script);
  _main := MainModule;
  repository := _main.repository ;
  runner := _main.runner;

  // cleanup
  lvRecipes.Clear;
  lvSubstitutions.Clear;

  pgVersionDetails.ActivePageIndex := 0;
  PopulateTestList;
end;

procedure TfrmMainWindow.FormDestroy(Sender: TObject);
begin
  RepositoryData.Destroy;
  script.Destroy;
end;

procedure TfrmMainWindow.LoadRecipe(Index: integer);
var
  version, substitutions, sub, pattern, replacement, v : Variant;
  i,j,k : integer;
  li : TListItem;
  s : string;
begin
  version := Test.versions.GetItem(Index) ;
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
  cbDialect.ItemIndex := cbDialect.Items.IndexOf(version.sql_dialect) ;

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

  btnEditRecipe.Enabled := True;
  btnDeleteRecipe.Enabled := True;
end;

procedure TfrmMainWindow.LoadTest(Id: string);
var
  versions, version : Variant;
  i : integer;
  li : TListItem;
begin
  Test := Repository.get_test(Id);

  edTestID.Text := Test.id ;
  edTitle.Text := Test.title ;
  edTrackerID.Text := Test.tracker_id ;
  if Test.min_versions = None then
    edMinVersions.Text := ''
  else
    edMinVersions.Text := Test.min_versions;
  memoDescription.Lines.Text := Test.description ;
  versions := Test.versions ;
  lvRecipes.Items.Clear;
  for i := 0 to len(versions)-1 do
  begin
      version := versions.GetItem(i) ;
      li := lvRecipes.Items.Add ;
      li.Caption := version.firebird_version ;
      li.Data := Pointer(i);
      li.SubItems.Add(version.platform) ;
  end;
  lvRecipes.Selected := lvRecipes.Items[0];
  btnEditTest.Enabled := True;
  btnReloadTest.Enabled := True;
  btnNewRecipe.Enabled := True;
  btnExecute.Enabled := True;
end;

procedure TfrmMainWindow.lvRecipesSelectItem(Sender: TObject; Item: TListItem;
  Selected: Boolean);
begin
  if Selected then
    LoadRecipe(Integer(Item.Data));
end;

procedure TfrmMainWindow.PopulateTestList;

  procedure AddSuite(ParentNode: TTreeNode; Suite : Variant) ;
  var
    V, Suites, Tests : Variant;
    ChildNode : TTreeNode;
    i : integer;
    Info : TRepositoryInfo ;
  begin
    Suites := Suite.suites.values();
    Tests := Suite.tests;
    for i := 0 to len(Suites) - 1 do begin
      V := Suites.GetItem(i) ;
      Info := TRepositoryInfo.Create(riSuite,V.get_id(),V.name);
      ChildNode := treeRepository.Items.AddChild(ParentNode,Info.Name) ;
      ChildNode.Data := Info;
      ChildNode.ImageIndex := 0;
      ChildNode.SelectedIndex := 0;
      AddSuite(ChildNode,Suite.suites.GetItem(Info.Name));
    end;
    for i := 0 to len(Tests) - 1 do begin
      V := Tests.GetItem(i) ;
      Info := TRepositoryInfo.Create(riTest,V.id,V.get_name());
      ChildNode := treeRepository.Items.AddChild(ParentNode,Info.Name) ;
      ChildNode.Data := Info;
      ChildNode.ImageIndex := 1;
      ChildNode.SelectedIndex := 1;
    end;
  end;

begin
  treeRepository.Items.Clear;
  RepositoryData.Clear;
  AddSuite(nil,Repository.suite);
end;

procedure TfrmMainWindow.Print(s: string);
begin
  memoPythonOutput.Lines.Append(s);
end;

procedure TfrmMainWindow.PrintList(l: variant);
var
  i : integer;
begin
  for i:= 0 to len(l) - 1 do
    memoPythonOutput.Lines.Append(l.GetItem(i));
end;

procedure TfrmMainWindow.PythonEngine1BeforeLoad(Sender: TObject);
begin
//  PythonEngine1.DllPath := ExtractFilePath(Application.ExeName);
//  PythonEngine1.DllName := 'python25-fb.dll';
end;

procedure TfrmMainWindow.PythonEngine1PathInitialization(Sender: TObject;
  var Path: string);
begin
  Path := '.;.\\DLL;.\\Lib';
end;

procedure TfrmMainWindow.PythonEngine1SysPathInit(Sender: TObject;
  PathList: PPyObject);
begin
  memoPythonOutput.Lines.Append(PythonEngine1.PyObjectAsString(PathList));
end;

procedure TfrmMainWindow.treeRepositoryChange(Sender: TObject; Node: TTreeNode);
var
  Info : TRepositoryInfo;
begin
  Info := TRepositoryInfo(Node.Data) ;
  if Info.Kind = riTest then begin
    LoadTest(Info.Id);
  end;
end;

{ TRepositoryInfo }

constructor TRepositoryInfo.Create(AKind: TRepositoryInfoType; AId,
  AName: string);
begin
  Kind := AKind;
  Name := AName;
  Id := AId;
end;

end.
