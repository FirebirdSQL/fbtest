object frmMainWindow: TfrmMainWindow
  Left = 0
  Top = 0
  Caption = 'Firebird Test Editor'
  ClientHeight = 541
  ClientWidth = 730
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'MS Shell Dlg 2'
  Font.Style = []
  OldCreateOrder = False
  Position = poDesktopCenter
  OnCreate = FormCreate
  OnDestroy = FormDestroy
  PixelsPerInch = 96
  TextHeight = 13
  object Splitter2: TSplitter
    Left = 0
    Top = 472
    Width = 730
    Height = 5
    Cursor = crVSplit
    Align = alBottom
    Beveled = True
    ExplicitTop = 562
    ExplicitWidth = 746
  end
  object Panel2: TPanel
    Left = 0
    Top = 0
    Width = 730
    Height = 472
    Align = alClient
    BevelOuter = bvNone
    TabOrder = 0
    object Splitter1: TSplitter
      Left = 185
      Top = 0
      Width = 5
      Height = 472
      Beveled = True
      ExplicitLeft = 186
      ExplicitTop = 1
      ExplicitHeight = 560
    end
    object pnTest: TPanel
      Left = 190
      Top = 0
      Width = 540
      Height = 472
      Align = alClient
      BevelOuter = bvNone
      Constraints.MinWidth = 500
      Ctl3D = True
      ParentCtl3D = False
      TabOrder = 0
      object Splitter3: TSplitter
        Left = 0
        Top = 217
        Width = 540
        Height = 5
        Cursor = crVSplit
        Align = alTop
        Beveled = True
        ExplicitTop = 85
        ExplicitWidth = 556
      end
      object pnCommands: TPanel
        Left = 0
        Top = 415
        Width = 540
        Height = 57
        Align = alBottom
        BevelInner = bvLowered
        BevelOuter = bvNone
        TabOrder = 0
        object gbTest: TGroupBox
          Left = 6
          Top = 1
          Width = 206
          Height = 50
          Caption = 'Test'
          TabOrder = 0
          object btnEditTest: TButton
            Left = 6
            Top = 18
            Width = 60
            Height = 25
            Caption = 'Edit'
            Enabled = False
            TabOrder = 0
            OnClick = btnEditTestClick
          end
          object btnNewTest: TButton
            Left = 72
            Top = 18
            Width = 60
            Height = 25
            Caption = 'New'
            TabOrder = 1
            OnClick = btnNewTestClick
          end
          object btnReloadTest: TButton
            Left = 138
            Top = 18
            Width = 60
            Height = 25
            Caption = 'Reload'
            TabOrder = 2
            OnClick = btnReloadTestClick
          end
        end
        object gbRecipe: TGroupBox
          Left = 218
          Top = 1
          Width = 210
          Height = 50
          Caption = 'Recipe'
          TabOrder = 1
          object btnEditRecipe: TButton
            Left = 7
            Top = 19
            Width = 60
            Height = 25
            Caption = 'Edit'
            Enabled = False
            TabOrder = 0
            OnClick = btnEditRecipeClick
          end
          object btnNewRecipe: TButton
            Left = 74
            Top = 19
            Width = 60
            Height = 25
            Caption = 'New'
            Enabled = False
            TabOrder = 1
            OnClick = btnNewRecipeClick
          end
          object btnDeleteRecipe: TButton
            Left = 141
            Top = 19
            Width = 60
            Height = 25
            Caption = 'Delete'
            Enabled = False
            TabOrder = 2
            OnClick = btnDeleteRecipeClick
          end
        end
        object gbSpecial: TGroupBox
          Left = 456
          Top = 1
          Width = 73
          Height = 50
          Caption = 'Special'
          TabOrder = 2
          object btnExecute: TButton
            Left = 8
            Top = 18
            Width = 60
            Height = 25
            Caption = 'Execute'
            Enabled = False
            TabOrder = 0
            OnClick = btnExecuteClick
          end
        end
      end
      object pnTestHeader: TPanel
        Left = 0
        Top = 0
        Width = 540
        Height = 217
        Align = alTop
        BevelOuter = bvNone
        TabOrder = 1
        object lvRecipes: TListView
          Left = 268
          Top = 98
          Width = 272
          Height = 119
          Align = alRight
          BevelInner = bvNone
          BevelOuter = bvNone
          Columns = <
            item
              Caption = 'Version'
            end
            item
              Caption = 'Platforms'
              Width = 200
            end>
          ColumnClick = False
          Constraints.MinWidth = 270
          Ctl3D = False
          FlatScrollBars = True
          GridLines = True
          HideSelection = False
          Items.ItemData = {
            01AB0000000300000000000000FFFFFFFFFFFFFFFF0100000000000000033100
            2E0030000341006C006C0000000000FFFFFFFFFFFFFFFF010000000000000005
            32002E0031002E00310007570069006E0064006F007700730000000000FFFFFF
            FFFFFFFFFF01000000000000000532002E0031002E003100194C0069006E0075
            0078003A004D00610063004F0053003A0046007200650065004200530044003A
            00480050002D0055005800FFFFFFFFFFFF}
          ReadOnly = True
          RowSelect = True
          TabOrder = 0
          ViewStyle = vsReport
          OnSelectItem = lvRecipesSelectItem
        end
        object memoDescription: TTntMemo
          Left = 0
          Top = 98
          Width = 261
          Height = 119
          Align = alClient
          BevelInner = bvNone
          BevelOuter = bvNone
          Constraints.MinHeight = 80
          Constraints.MinWidth = 250
          Ctl3D = False
          ParentCtl3D = False
          ReadOnly = True
          ScrollBars = ssVertical
          TabOrder = 1
        end
        object pnTestHeaderFields: TPanel
          Left = 0
          Top = 0
          Width = 540
          Height = 98
          Align = alTop
          BevelOuter = bvNone
          TabOrder = 2
          DesignSize = (
            540
            98)
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
          object lblRecipes: TLabel
            Left = 281
            Top = 82
            Width = 41
            Height = 13
            Caption = 'Recipes:'
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
            Width = 470
            Height = 19
            Anchors = [akLeft, akTop, akRight]
            BevelOuter = bvNone
            Ctl3D = False
            ParentCtl3D = False
            ReadOnly = True
            TabOrder = 0
          end
          object edTitle: TTntEdit
            Left = 64
            Top = 32
            Width = 470
            Height = 19
            Anchors = [akLeft, akTop, akRight]
            Ctl3D = False
            ParentCtl3D = False
            ReadOnly = True
            TabOrder = 1
          end
          object edTrackerID: TTntEdit
            Left = 64
            Top = 57
            Width = 129
            Height = 19
            Ctl3D = False
            ParentCtl3D = False
            ReadOnly = True
            TabOrder = 2
          end
          object edMinVersions: TTntEdit
            Left = 268
            Top = 57
            Width = 266
            Height = 19
            Ctl3D = False
            ParentCtl3D = False
            ReadOnly = True
            TabOrder = 3
          end
        end
        object pnSeparator1: TPanel
          Left = 261
          Top = 98
          Width = 7
          Height = 119
          Align = alRight
          BevelOuter = bvNone
          BorderWidth = 5
          TabOrder = 3
        end
      end
      object pgVersionDetails: TPageControl
        Left = 0
        Top = 222
        Width = 540
        Height = 193
        ActivePage = tabVersion
        Align = alClient
        Constraints.MinHeight = 193
        Constraints.MinWidth = 540
        Style = tsFlatButtons
        TabOrder = 2
        object tabVersion: TTabSheet
          Caption = 'Version'
          ImageIndex = 1
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
            Enabled = False
            ItemHeight = 13
            ItemIndex = 0
            ParentCtl3D = False
            TabOrder = 0
            Text = 'ISQL'
            Items.Strings = (
              'ISQL'
              'Python')
          end
          object lbResources: TListBox
            Left = 227
            Top = 50
            Width = 302
            Height = 110
            Ctl3D = False
            Enabled = False
            ItemHeight = 13
            ParentCtl3D = False
            TabOrder = 1
          end
          object chklbPlatforms: TCheckListBox
            Left = 3
            Top = 50
            Width = 205
            Height = 110
            Ctl3D = False
            Enabled = False
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
            ReadOnly = True
            TabOrder = 3
          end
        end
        object tabDatabase: TTabSheet
          Caption = 'Database'
          ImageIndex = 2
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
            Enabled = False
            ItemHeight = 13
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
            ReadOnly = True
            TabOrder = 1
          end
          object edBackupFile: TEdit
            Left = 64
            Top = 65
            Width = 225
            Height = 19
            Ctl3D = False
            ParentCtl3D = False
            ReadOnly = True
            TabOrder = 2
          end
          object edUserName: TEdit
            Left = 64
            Top = 104
            Width = 121
            Height = 19
            Ctl3D = False
            ParentCtl3D = False
            ReadOnly = True
            TabOrder = 3
          end
          object edUserPassword: TEdit
            Left = 64
            Top = 129
            Width = 121
            Height = 19
            Ctl3D = False
            ParentCtl3D = False
            ReadOnly = True
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
            Enabled = False
            ItemHeight = 13
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
            Enabled = False
            ItemHeight = 13
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
            Enabled = False
            ItemHeight = 13
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
            Enabled = False
            ItemHeight = 13
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
          object memoInitScript: TTntMemo
            Left = 0
            Top = 0
            Width = 532
            Height = 162
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
        object TabSheet4: TTabSheet
          Caption = 'Test Script'
          ImageIndex = 4
          object memoTestScript: TTntMemo
            Left = 0
            Top = 0
            Width = 532
            Height = 162
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
          object memoStdOut: TTntMemo
            Left = 0
            Top = 0
            Width = 532
            Height = 162
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
          object memoStdErr: TTntMemo
            Left = 0
            Top = 0
            Width = 532
            Height = 162
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
        object tabSubstitutions: TTabSheet
          Caption = 'Substitutions'
          ImageIndex = 6
          object Panel7: TPanel
            Left = 0
            Top = 0
            Width = 532
            Height = 162
            Align = alClient
            BevelOuter = bvNone
            Caption = 'Panel7'
            TabOrder = 0
            object lvSubstitutions: TTntListView
              Left = 0
              Top = 0
              Width = 532
              Height = 162
              Align = alClient
              Columns = <
                item
                  Caption = 'Pattern'
                  Width = 250
                end
                item
                  Caption = 'Replacement'
                  Width = 250
                end>
              ColumnClick = False
              FlatScrollBars = True
              GridLines = True
              Items.ItemData = {
                018A0000000200000000000000FFFFFFFFFFFFFFFF0100000000000000095000
                610074007400650072006E00200030000D5200650070006C006100630065006D
                0065006E0074002000300000000000FFFFFFFFFFFFFFFF010000000000000009
                5000610074007400650072006E00200031000D5200650070006C006100630065
                006D0065006E00740020003100FFFFFFFF}
              RowSelect = True
              TabOrder = 0
              ViewStyle = vsReport
              ExplicitWidth = 464
              ExplicitHeight = 149
            end
          end
        end
      end
    end
    object pnTreeList: TPanel
      Left = 0
      Top = 0
      Width = 185
      Height = 472
      Align = alLeft
      TabOrder = 1
      object treeRepository: TTreeView
        Left = 1
        Top = 1
        Width = 183
        Height = 470
        Align = alClient
        AutoExpand = True
        Constraints.MinWidth = 150
        Images = imglRepository
        Indent = 19
        ReadOnly = True
        ShowRoot = False
        TabOrder = 0
        OnChange = treeRepositoryChange
      end
    end
  end
  object memoPythonOutput: TTntMemo
    Left = 0
    Top = 477
    Width = 730
    Height = 64
    Align = alBottom
    Constraints.MinHeight = 60
    ScrollBars = ssBoth
    TabOrder = 1
    WordWrap = False
  end
  object PythonEngine1: TPythonEngine
    DllPath = '.'
    OnBeforeLoad = PythonEngine1BeforeLoad
    InitScript.Strings = (
      'import sys'
      'import os'
      'print "Python path =", sys.path'
      'print'
      'print "PYTHONHOME =", os.getenv('#39'PYTHONHOME'#39')'
      'print "PYTHONPATH =", os.getenv('#39'PYTHONPATH'#39')'
      'print'
      'print "Python modules already imported:"'
      'for m in sys.modules.values():'
      '  if m:'
      '    print " ", m')
    IO = PythonGUIInputOutput1
    PyFlags = [pfIgnoreEnvironmentFlag]
    OnPathInitialization = PythonEngine1PathInitialization
    OnSysPathInit = PythonEngine1SysPathInit
    Left = 40
    Top = 496
  end
  object PythonGUIInputOutput1: TPythonGUIInputOutput
    UnicodeIO = False
    RawOutput = False
    Output = memoPythonOutput
    Left = 8
    Top = 496
  end
  object OpenDialog1: TOpenDialog
    DefaultExt = 'fbt'
    Filter = 'Firebird test|*.fbt|All files|*.*'
    Options = [ofPathMustExist, ofFileMustExist, ofEnableSizing]
    Left = 72
    Top = 496
  end
  object imglRepository: TImageList
    ImageType = itMask
    Left = 32
    Top = 376
    Bitmap = {
      494C010102000400040010001000FFFFFFFFFF00FFFFFFFFFFFFFFFF424D3600
      0000000000003600000028000000400000001000000001002000000000000010
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFF
      FF00000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000FFFFFF0000000000000000000000000000000000FFFFFF00FFFFFF00FFFF
      FF00000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFF
      FF00000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      00000000000000000000000000000000000000000000000000000000000000FF
      FF00BFBFBF0000FFFF00BFBFBF0000FFFF00BFBFBF0000FFFF00BFBFBF0000FF
      FF00000000000000000000000000000000000000000000000000000000000000
      0000FFFFFF00000000000000000000000000000000000000000000000000FFFF
      FF00000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000FFFFFF000000
      000000FFFF00BFBFBF0000FFFF00BFBFBF0000FFFF00BFBFBF0000FFFF00BFBF
      BF0000FFFF000000000000000000000000000000000000000000000000000000
      0000FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFF
      FF00000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      000000000000000000000000000000000000000000000000000000FFFF00FFFF
      FF000000000000FFFF00BFBFBF0000FFFF00BFBFBF0000FFFF00BFBFBF0000FF
      FF00BFBFBF0000FFFF0000000000000000000000000000000000000000000000
      0000FFFFFF00000000000000000000000000000000000000000000000000FFFF
      FF00000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000FFFFFF0000FF
      FF00FFFFFF000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFF
      FF00000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      000000000000000000000000000000000000000000000000000000FFFF00FFFF
      FF0000FFFF00FFFFFF0000FFFF00FFFFFF0000FFFF00FFFFFF0000FFFF000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000FFFFFF00000000000000000000000000FFFFFF00FFFFFF00FFFFFF00FFFF
      FF00000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000FFFFFF0000FF
      FF00FFFFFF0000FFFF00FFFFFF0000FFFF00FFFFFF0000FFFF00FFFFFF000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF0000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      000000000000000000000000000000000000000000000000000000FFFF00FFFF
      FF0000FFFF00FFFFFF0000FFFF00FFFFFF000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000FFFFFF000000000000000000FFFFFF00FFFFFF0000000000FFFFFF000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      00000000000000000000000000000000000000000000000000000000000000FF
      FF00FFFFFF0000FFFF00FFFFFF00000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF0000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      00000000000000000000000000000000000000000000000000007F7F7F000000
      00000000000000000000000000007F7F7F000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      0000000000000000000000000000000000000000000000000000000000000000
      000000000000000000000000000000000000424D3E000000000000003E000000
      2800000040000000100000000100010000000000800000000000000000000000
      000000000000000000000000FFFFFF00FFFFFFFF00000000FFFFE00700000000
      FFFFE00700000000FFFFE00700000000C00FE007000000008007E00700000000
      8003E007000000008001E007000000008001E00700000000800FE00700000000
      800FE00700000000801FE00F00000000C0FFE01F00000000C0FFE03F00000000
      FFFFFFFF00000000FFFFFFFF00000000}
  end
end
