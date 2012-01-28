program fbtedit;

uses
  Forms,
  fMain in 'fMain.pas' {frmMainWindow},
  fTestEdit in 'fTestEdit.pas' {frmEditTest},
  fRecipeEdit in 'fRecipeEdit.pas' {frmEditRecipe},
  fRunResult in 'fRunResult.pas' {dlgResult};

{$R *.res}

begin
  Application.Initialize;
  Application.Title := 'Firebird Test Editor';
  Application.CreateForm(TfrmMainWindow, frmMainWindow);
  Application.Run;
end.
