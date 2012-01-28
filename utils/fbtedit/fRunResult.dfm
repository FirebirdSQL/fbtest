object dlgResult: TdlgResult
  Left = 0
  Top = 0
  Caption = 'dlgResult'
  ClientHeight = 350
  ClientWidth = 554
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  Position = poOwnerFormCenter
  PixelsPerInch = 96
  TextHeight = 13
  object pnCommands: TPanel
    Left = 0
    Top = 310
    Width = 554
    Height = 40
    Align = alBottom
    BevelInner = bvLowered
    BevelOuter = bvNone
    TabOrder = 0
    object btnCancel: TButton
      Left = 275
      Top = 6
      Width = 75
      Height = 25
      Cancel = True
      Caption = 'Close'
      Default = True
      ModalResult = 2
      TabOrder = 0
    end
    object btnSave: TButton
      Left = 183
      Top = 6
      Width = 75
      Height = 25
      Caption = 'Save'
      ModalResult = 1
      TabOrder = 1
      OnClick = btnSaveClick
    end
  end
  object pgResult: TPageControl
    Left = 0
    Top = 0
    Width = 554
    Height = 310
    ActivePage = tabResult
    Align = alClient
    Constraints.MinHeight = 193
    Constraints.MinWidth = 540
    Style = tsFlatButtons
    TabOrder = 1
    object tabResult: TTabSheet
      Caption = 'Result'
      ImageIndex = 6
      object memoResult: TTntMemo
        Left = 0
        Top = 0
        Width = 546
        Height = 279
        Align = alClient
        BevelInner = bvNone
        BevelOuter = bvNone
        Constraints.MinHeight = 80
        Ctl3D = False
        Font.Charset = EASTEUROPE_CHARSET
        Font.Color = clWindowText
        Font.Height = -13
        Font.Name = 'Courier New'
        Font.Style = []
        ParentCtl3D = False
        ParentFont = False
        ReadOnly = True
        ScrollBars = ssBoth
        TabOrder = 0
        WordWrap = False
      end
    end
    object tabStdOut: TTabSheet
      Caption = 'StdOut'
      ImageIndex = 4
      ExplicitLeft = 0
      ExplicitTop = 0
      ExplicitWidth = 0
      ExplicitHeight = 0
      object memoStdOut: TTntMemo
        Left = 0
        Top = 0
        Width = 546
        Height = 279
        Align = alClient
        BevelInner = bvNone
        BevelOuter = bvNone
        Constraints.MinHeight = 80
        Ctl3D = False
        Font.Charset = EASTEUROPE_CHARSET
        Font.Color = clWindowText
        Font.Height = -13
        Font.Name = 'Courier New'
        Font.Style = []
        ParentCtl3D = False
        ParentFont = False
        ReadOnly = True
        ScrollBars = ssBoth
        TabOrder = 0
        WordWrap = False
      end
    end
    object tabStdOutExpected: TTabSheet
      Caption = 'StdOut Expected'
      ImageIndex = 3
      ExplicitLeft = 0
      ExplicitTop = 0
      ExplicitWidth = 0
      ExplicitHeight = 0
      object memoStdOutExpected: TTntMemo
        Left = 0
        Top = 0
        Width = 546
        Height = 279
        Align = alClient
        BevelInner = bvNone
        BevelOuter = bvNone
        Constraints.MinHeight = 80
        Ctl3D = False
        Font.Charset = EASTEUROPE_CHARSET
        Font.Color = clWindowText
        Font.Height = -13
        Font.Name = 'Courier New'
        Font.Style = []
        ParentCtl3D = False
        ParentFont = False
        ReadOnly = True
        ScrollBars = ssBoth
        TabOrder = 0
        WordWrap = False
      end
    end
    object tabStdOutDiff: TTabSheet
      Caption = 'StdOut Diff'
      ImageIndex = 4
      ExplicitLeft = 0
      ExplicitTop = 0
      ExplicitWidth = 0
      ExplicitHeight = 0
      object memoStdOutDiff: TTntMemo
        Left = 0
        Top = 0
        Width = 546
        Height = 279
        Align = alClient
        BevelInner = bvNone
        BevelOuter = bvNone
        Constraints.MinHeight = 80
        Ctl3D = False
        Font.Charset = EASTEUROPE_CHARSET
        Font.Color = clWindowText
        Font.Height = -13
        Font.Name = 'Courier New'
        Font.Style = []
        ParentCtl3D = False
        ParentFont = False
        ReadOnly = True
        ScrollBars = ssBoth
        TabOrder = 0
        WordWrap = False
      end
    end
    object tabStdErr: TTabSheet
      Caption = 'StdErr'
      ImageIndex = 5
      ExplicitLeft = 0
      ExplicitTop = 0
      ExplicitWidth = 0
      ExplicitHeight = 0
      object memoStdErr: TTntMemo
        Left = 0
        Top = 0
        Width = 546
        Height = 279
        Align = alClient
        BevelInner = bvNone
        BevelOuter = bvNone
        Constraints.MinHeight = 80
        Ctl3D = False
        Font.Charset = EASTEUROPE_CHARSET
        Font.Color = clWindowText
        Font.Height = -13
        Font.Name = 'Courier New'
        Font.Style = []
        ParentCtl3D = False
        ParentFont = False
        ReadOnly = True
        ScrollBars = ssBoth
        TabOrder = 0
        WordWrap = False
      end
    end
    object tabStdErrExcpected: TTabSheet
      Caption = 'StdErr Expected'
      ImageIndex = 4
      ExplicitLeft = 0
      ExplicitTop = 0
      ExplicitWidth = 0
      ExplicitHeight = 0
      object memoStdErrExpected: TTntMemo
        Left = 0
        Top = 0
        Width = 546
        Height = 279
        Align = alClient
        BevelInner = bvNone
        BevelOuter = bvNone
        Constraints.MinHeight = 80
        Ctl3D = False
        Font.Charset = EASTEUROPE_CHARSET
        Font.Color = clWindowText
        Font.Height = -13
        Font.Name = 'Courier New'
        Font.Style = []
        ParentCtl3D = False
        ParentFont = False
        ReadOnly = True
        ScrollBars = ssBoth
        TabOrder = 0
        WordWrap = False
      end
    end
    object tabStdErrDiff: TTabSheet
      Caption = 'StdErr Diff'
      ImageIndex = 5
      ExplicitLeft = 0
      ExplicitTop = 0
      ExplicitWidth = 0
      ExplicitHeight = 0
      object memoStdErrDiff: TTntMemo
        Left = 0
        Top = 0
        Width = 546
        Height = 279
        Align = alClient
        BevelInner = bvNone
        BevelOuter = bvNone
        Constraints.MinHeight = 80
        Ctl3D = False
        Font.Charset = EASTEUROPE_CHARSET
        Font.Color = clWindowText
        Font.Height = -13
        Font.Name = 'Courier New'
        Font.Style = []
        ParentCtl3D = False
        ParentFont = False
        ReadOnly = True
        ScrollBars = ssBoth
        TabOrder = 0
        WordWrap = False
      end
    end
  end
end
