object frmEditRecipe: TfrmEditRecipe
  Left = 0
  Top = 0
  Caption = 'frmEditRecipe'
  ClientHeight = 374
  ClientWidth = 554
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
  object pnTest: TPanel
    Left = 0
    Top = 0
    Width = 554
    Height = 374
    Align = alClient
    BevelOuter = bvNone
    Constraints.MinWidth = 500
    Ctl3D = True
    ParentCtl3D = False
    TabOrder = 0
    object pnCommands: TPanel
      Left = 0
      Top = 334
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
        Caption = 'Cancel'
        ModalResult = 2
        TabOrder = 1
        OnClick = btnCancelClick
      end
      object btnSave: TButton
        Left = 183
        Top = 6
        Width = 75
        Height = 25
        Caption = 'Save'
        Default = True
        ModalResult = 1
        TabOrder = 0
        OnClick = btnSaveClick
      end
    end
    object pgVersionDetails: TPageControl
      Left = 0
      Top = 0
      Width = 554
      Height = 334
      ActivePage = tabSubstitutions
      Align = alClient
      Constraints.MinHeight = 193
      Constraints.MinWidth = 540
      Style = tsFlatButtons
      TabOrder = 1
      object tabVersion: TTabSheet
        Caption = 'Version'
        ImageIndex = 1
        ExplicitLeft = 0
        ExplicitTop = 0
        ExplicitWidth = 532
        ExplicitHeight = 0
        object lblFirebirdVersion: TLabel
          Left = 3
          Top = 6
          Width = 78
          Height = 13
          Caption = 'Firebird Version:'
        end
        object lblPlatforms: TLabel
          Left = 3
          Top = 35
          Width = 49
          Height = 13
          Caption = 'Platforms:'
        end
        object lblTestType: TLabel
          Left = 227
          Top = 6
          Width = 52
          Height = 13
          Caption = 'Test Type:'
        end
        object lblResources: TLabel
          Left = 227
          Top = 35
          Width = 54
          Height = 13
          Caption = 'Resources:'
        end
        object cbTestType: TComboBox
          Left = 285
          Top = 3
          Width = 145
          Height = 21
          BevelEdges = []
          BevelInner = bvNone
          BevelOuter = bvNone
          Style = csDropDownList
          Ctl3D = False
          ItemHeight = 0
          ItemIndex = 0
          ParentCtl3D = False
          TabOrder = 1
          Text = 'ISQL'
          Items.Strings = (
            'ISQL'
            'Python')
        end
        object lbResources: TListBox
          Left = 227
          Top = 50
          Width = 203
          Height = 110
          Ctl3D = False
          ItemHeight = 13
          ParentCtl3D = False
          TabOrder = 3
          OnClick = lbResourcesClick
        end
        object chklbPlatforms: TCheckListBox
          Left = 3
          Top = 50
          Width = 205
          Height = 110
          Ctl3D = False
          ItemHeight = 13
          Items.Strings = (
            'Windows'
            'Linux'
            'MacOS'
            'Solaris'
            'FreeBSD'
            'HP-UX')
          ParentCtl3D = False
          TabOrder = 2
        end
        object edFirebirdVersion: TEdit
          Left = 87
          Top = 3
          Width = 121
          Height = 19
          Ctl3D = False
          ParentCtl3D = False
          TabOrder = 0
        end
        object btnNewResource: TButton
          Left = 436
          Top = 72
          Width = 75
          Height = 25
          Caption = 'New'
          TabOrder = 4
          OnClick = btnNewResourceClick
        end
        object btnDeleteResource: TButton
          Left = 436
          Top = 112
          Width = 75
          Height = 25
          Caption = 'Delete'
          Enabled = False
          TabOrder = 5
          OnClick = btnDeleteResourceClick
        end
      end
      object tabDatabase: TTabSheet
        Caption = 'Database'
        ImageIndex = 2
        ExplicitLeft = 0
        ExplicitTop = 0
        ExplicitWidth = 532
        ExplicitHeight = 0
        object lblDatabase: TLabel
          Left = 1
          Top = 3
          Width = 50
          Height = 13
          Caption = 'Database:'
        end
        object lblDatabaseName: TLabel
          Left = 1
          Top = 42
          Width = 47
          Height = 13
          Caption = 'Db Name:'
        end
        object lblBackupFile: TLabel
          Left = 1
          Top = 67
          Width = 57
          Height = 13
          Caption = 'Backup File:'
        end
        object lblUserName: TLabel
          Left = 1
          Top = 106
          Width = 26
          Height = 13
          Caption = 'User:'
        end
        object lblUserPassword: TLabel
          Left = 1
          Top = 131
          Width = 50
          Height = 13
          Caption = 'Password:'
        end
        object lblDbCharset: TLabel
          Left = 201
          Top = 106
          Width = 58
          Height = 13
          Caption = 'Db Charset:'
        end
        object lblConnectionCharset: TLabel
          Left = 201
          Top = 133
          Width = 74
          Height = 13
          Caption = 'Conn. Charset:'
        end
        object lblPageSize: TLabel
          Left = 407
          Top = 133
          Width = 50
          Height = 13
          Caption = 'Page Size:'
        end
        object lblDialect: TLabel
          Left = 407
          Top = 106
          Width = 58
          Height = 13
          Caption = 'SQL Dialect:'
        end
        object cbDatabase: TComboBox
          Left = 64
          Top = 0
          Width = 121
          Height = 21
          BevelInner = bvNone
          BevelOuter = bvNone
          Style = csDropDownList
          Ctl3D = False
          ItemHeight = 0
          ItemIndex = 0
          ParentCtl3D = False
          TabOrder = 0
          Text = 'New'
          Items.Strings = (
            'New'
            'Existing'
            'Restore')
        end
        object edDatabaseName: TEdit
          Left = 64
          Top = 40
          Width = 225
          Height = 19
          Ctl3D = False
          ParentCtl3D = False
          TabOrder = 1
        end
        object edBackupFile: TEdit
          Left = 64
          Top = 65
          Width = 225
          Height = 19
          Ctl3D = False
          ParentCtl3D = False
          TabOrder = 2
        end
        object edUserName: TEdit
          Left = 64
          Top = 104
          Width = 121
          Height = 19
          Ctl3D = False
          ParentCtl3D = False
          TabOrder = 3
        end
        object edUserPassword: TEdit
          Left = 64
          Top = 129
          Width = 121
          Height = 19
          Ctl3D = False
          ParentCtl3D = False
          TabOrder = 4
        end
        object cbDbCharset: TComboBox
          Left = 287
          Top = 103
          Width = 105
          Height = 21
          BevelInner = bvNone
          BevelOuter = bvNone
          Style = csDropDownList
          Ctl3D = False
          ItemHeight = 0
          ItemIndex = 1
          ParentCtl3D = False
          TabOrder = 5
          Text = 'NONE'
          Items.Strings = (
            ''
            'NONE'
            'ASCII'
            'BIG_5'
            'CYRL'
            'DOS437'
            'DOS737'
            'DOS775'
            'DOS850'
            'DOS852'
            'DOS857'
            'DOS858'
            'DOS860'
            'DOS861'
            'DOS862'
            'DOS863'
            'DOS864'
            'DOS865'
            'DOS866'
            'DOS869'
            'EUCJ_0208'
            'GBK'
            'GB_2312'
            'ISO8859_1'
            'ISO8859_2'
            'ISO8859_3'
            'ISO8859_4'
            'ISO8859_5'
            'ISO8859_6'
            'ISO8859_7'
            'ISO8859_8'
            'ISO8859_9'
            'ISO8859_13'
            'KOI8R'
            'KOI8U'
            'KSC_5601'
            'NEXT'
            'OCTETS'
            'SJIS_0208'
            'TIS620'
            'UNICODE_FSS'
            'UTF8'
            'WIN1250'
            'WIN1251'
            'WIN1252'
            'WIN1253'
            'WIN1254'
            'WIN1255'
            'WIN1256'
            'WIN1257'
            'WIN1258'
            'LATIN2')
        end
        object cbConnectionCharset: TComboBox
          Left = 287
          Top = 130
          Width = 105
          Height = 21
          BevelInner = bvNone
          BevelOuter = bvNone
          Style = csDropDownList
          Ctl3D = False
          ItemHeight = 0
          ItemIndex = 1
          ParentCtl3D = False
          TabOrder = 6
          Text = 'NONE'
          Items.Strings = (
            ''
            'NONE'
            'ASCII'
            'BIG_5'
            'CYRL'
            'DOS437'
            'DOS737'
            'DOS775'
            'DOS850'
            'DOS852'
            'DOS857'
            'DOS858'
            'DOS860'
            'DOS861'
            'DOS862'
            'DOS863'
            'DOS864'
            'DOS865'
            'DOS866'
            'DOS869'
            'EUCJ_0208'
            'GBK'
            'GB_2312'
            'ISO8859_1'
            'ISO8859_2'
            'ISO8859_3'
            'ISO8859_4'
            'ISO8859_5'
            'ISO8859_6'
            'ISO8859_7'
            'ISO8859_8'
            'ISO8859_9'
            'ISO8859_13'
            'KOI8R'
            'KOI8U'
            'KSC_5601'
            'NEXT'
            'OCTETS'
            'SJIS_0208'
            'TIS620'
            'UNICODE_FSS'
            'UTF8'
            'WIN1250'
            'WIN1251'
            'WIN1252'
            'WIN1253'
            'WIN1254'
            'WIN1255'
            'WIN1256'
            'WIN1257'
            'WIN1258'
            'LATIN2')
        end
        object cbPageSize: TComboBox
          Left = 472
          Top = 130
          Width = 57
          Height = 21
          BevelInner = bvNone
          BevelOuter = bvNone
          Style = csDropDownList
          Ctl3D = False
          ItemHeight = 0
          ItemIndex = 3
          ParentCtl3D = False
          TabOrder = 7
          Text = '4096'
          Items.Strings = (
            ''
            '1024'
            '2048'
            '4096'
            '8192'
            '16384'
            '')
        end
        object cbDialect: TComboBox
          Left = 471
          Top = 103
          Width = 58
          Height = 21
          BevelInner = bvNone
          BevelOuter = bvNone
          Style = csDropDownList
          Ctl3D = False
          ItemHeight = 0
          ItemIndex = 1
          ParentCtl3D = False
          TabOrder = 8
          Text = '3'
          Items.Strings = (
            '1'
            '3')
        end
      end
      object tabInitScript: TTabSheet
        Caption = 'Init Script'
        ImageIndex = 3
        ExplicitLeft = 0
        ExplicitTop = 0
        ExplicitWidth = 532
        ExplicitHeight = 0
        object memoInitScript: TTntMemo
          Left = 0
          Top = 0
          Width = 546
          Height = 303
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
          ScrollBars = ssBoth
          TabOrder = 0
          WordWrap = False
          ExplicitWidth = 532
        end
      end
      object TabSheet4: TTabSheet
        Caption = 'Test Script'
        ImageIndex = 4
        ExplicitLeft = 0
        ExplicitTop = 0
        ExplicitWidth = 532
        ExplicitHeight = 0
        object memoTestScript: TTntMemo
          Left = 0
          Top = 0
          Width = 546
          Height = 303
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
          ScrollBars = ssBoth
          TabOrder = 0
          WordWrap = False
          ExplicitWidth = 532
        end
      end
      object tabStdOut: TTabSheet
        Caption = 'StdOut'
        ImageIndex = 4
        ExplicitLeft = 0
        ExplicitTop = 0
        ExplicitWidth = 532
        ExplicitHeight = 0
        object memoStdOut: TTntMemo
          Left = 0
          Top = 0
          Width = 546
          Height = 303
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
          ScrollBars = ssBoth
          TabOrder = 0
          WordWrap = False
          ExplicitWidth = 532
        end
      end
      object tabStdErr: TTabSheet
        Caption = 'StdErr'
        ImageIndex = 5
        ExplicitLeft = 0
        ExplicitTop = 0
        ExplicitWidth = 532
        ExplicitHeight = 0
        object memoStdErr: TTntMemo
          Left = 0
          Top = 0
          Width = 546
          Height = 303
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
          ScrollBars = ssBoth
          TabOrder = 0
          WordWrap = False
          ExplicitWidth = 532
        end
      end
      object tabSubstitutions: TTabSheet
        Caption = 'Substitutions'
        ImageIndex = 6
        object Panel5: TPanel
          Left = 462
          Top = 0
          Width = 84
          Height = 303
          Align = alRight
          BevelOuter = bvNone
          TabOrder = 0
          object btnNewSub: TButton
            Left = 6
            Top = 0
            Width = 75
            Height = 25
            Caption = 'New'
            TabOrder = 0
            OnClick = btnNewSubClick
          end
          object btnDeleteSub: TButton
            Left = 6
            Top = 31
            Width = 75
            Height = 25
            Caption = 'Delete'
            Enabled = False
            TabOrder = 1
            OnClick = btnDeleteSubClick
          end
          object btnReplaceSub: TButton
            Left = 6
            Top = 119
            Width = 75
            Height = 25
            Caption = 'Replace'
            Enabled = False
            TabOrder = 2
            OnClick = btnReplaceSubClick
          end
        end
        object Panel7: TPanel
          Left = 0
          Top = 0
          Width = 462
          Height = 303
          Align = alClient
          BevelOuter = bvNone
          Caption = 'Panel7'
          Constraints.MinWidth = 462
          TabOrder = 1
          object Panel6: TPanel
            Left = 0
            Top = 246
            Width = 462
            Height = 57
            Align = alBottom
            BevelOuter = bvNone
            TabOrder = 0
            object lblPattern: TLabel
              Left = 1
              Top = 9
              Width = 40
              Height = 13
              Caption = 'Pattern:'
            end
            object lblReplacement: TLabel
              Left = 2
              Top = 37
              Width = 66
              Height = 13
              Caption = 'Replacement:'
            end
            object edPattern: TTntEdit
              Left = 74
              Top = 6
              Width = 384
              Height = 19
              Ctl3D = False
              ParentCtl3D = False
              TabOrder = 0
            end
            object edReplacement: TTntEdit
              Left = 74
              Top = 34
              Width = 384
              Height = 19
              Ctl3D = False
              ParentCtl3D = False
              TabOrder = 1
            end
          end
          object lvSubstitutions: TTntListView
            Left = 0
            Top = 0
            Width = 462
            Height = 246
            Align = alClient
            Columns = <
              item
                Caption = 'Pattern'
                Width = 225
              end
              item
                Caption = 'Replacement'
                Width = 225
              end>
            ColumnClick = False
            FlatScrollBars = True
            GridLines = True
            ReadOnly = True
            RowSelect = True
            TabOrder = 1
            ViewStyle = vsReport
            OnClick = lvSubstitutionsClick
          end
        end
      end
    end
  end
end
