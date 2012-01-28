object frmEditTest: TfrmEditTest
  Left = 0
  Top = 0
  Caption = 'Test Information'
  ClientHeight = 341
  ClientWidth = 512
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  Position = poMainFormCenter
  PixelsPerInch = 96
  TextHeight = 13
  object pnTestHeaderFields: TPanel
    Left = 0
    Top = 0
    Width = 512
    Height = 300
    Align = alClient
    BevelOuter = bvNone
    TabOrder = 0
    DesignSize = (
      512
      300)
    object lblTestID: TLabel
      Left = 19
      Top = 9
      Width = 39
      Height = 13
      Caption = 'Test ID:'
    end
    object lblTitle: TLabel
      Left = 34
      Top = 34
      Width = 24
      Height = 13
      Caption = 'Title:'
    end
    object lblTrackerID: TLabel
      Left = 5
      Top = 59
      Width = 54
      Height = 13
      Caption = 'Tracker ID:'
    end
    object lblDescription: TLabel
      Left = 5
      Top = 82
      Width = 57
      Height = 13
      Caption = 'Description:'
    end
    object lblMinVersions: TLabel
      Left = 198
      Top = 59
      Width = 67
      Height = 13
      Caption = 'Min. Versions:'
    end
    object edTestID: TTntEdit
      Left = 64
      Top = 7
      Width = 442
      Height = 19
      Anchors = [akLeft, akTop, akRight]
      BevelOuter = bvNone
      Ctl3D = False
      Enabled = False
      ParentCtl3D = False
      ReadOnly = True
      TabOrder = 0
    end
    object edTitle: TTntEdit
      Left = 64
      Top = 32
      Width = 442
      Height = 19
      Anchors = [akLeft, akTop, akRight]
      Ctl3D = False
      ParentCtl3D = False
      TabOrder = 1
    end
    object edTrackerID: TTntEdit
      Left = 64
      Top = 57
      Width = 129
      Height = 19
      Ctl3D = False
      ParentCtl3D = False
      TabOrder = 2
    end
    object memoDescription: TTntMemo
      Left = 0
      Top = 104
      Width = 512
      Height = 196
      Align = alBottom
      BevelInner = bvNone
      BevelOuter = bvNone
      Constraints.MinHeight = 80
      Constraints.MinWidth = 250
      Ctl3D = False
      ParentCtl3D = False
      ScrollBars = ssVertical
      TabOrder = 4
    end
    object edMinVersions: TTntEdit
      Left = 271
      Top = 57
      Width = 235
      Height = 19
      Ctl3D = False
      ParentCtl3D = False
      TabOrder = 3
    end
  end
  object pnCommands: TPanel
    Left = 0
    Top = 300
    Width = 512
    Height = 41
    Align = alBottom
    TabOrder = 1
    object btnSave: TButton
      Left = 160
      Top = 8
      Width = 75
      Height = 25
      Caption = 'Save'
      ModalResult = 1
      TabOrder = 0
      OnClick = btnSaveClick
    end
    object btnCancel: TButton
      Left = 248
      Top = 8
      Width = 75
      Height = 25
      Cancel = True
      Caption = 'Cancel'
      ModalResult = 2
      TabOrder = 1
      OnClick = btnCancelClick
    end
  end
end
