Attribute VB_Name = "Module10"
Sub InsertPNGplotnost()
    Dim wdRange As Range
    Dim shape As InlineShape
    Dim folderPath As String
    Dim fileName As String
    Dim searchPattern As String
    Dim userInput As String
    Dim regex As Object
    Dim doc As Document
    Set regex = CreateObject("VBScript.RegExp")
    
    ' Просим пользователя ввести ID сценария
    userInput = InputBox("Введите ID сценария:")
    
    ' Путь к PNG тот же, что и к DOCX, в котором выполняется скрипт
    folderPath = ActiveDocument.Path & "\"
    Set doc = ActiveDocument
    
    ' Определяем паттерн имени
    searchPattern = "^peoples_detailed_\d{6}_\d_" & userInput & "\.png$"
    
    ' Регексим
    With regex
        .Global = False
        .IgnoreCase = True
        .pattern = searchPattern
    End With
    
    ' Проходимося по файлам в папке
    fileName = Dir(folderPath & "*.png")
    Do While fileName <> ""
        If regex.Test(fileName) Then
            ' Находим файл, который удовлетворяет паттерну имени
            Dim fileToInsert As String
            fileToInsert = folderPath & fileName

            ' Находим плейсхолдер
            Set wdRange = doc.Content
            With wdRange.Find
                .text = "[[SC_PLOTNOST]]"
                .Forward = True
                .Wrap = wdFindStop
                .Format = False
                .Execute

                ' Если плейсхолдер найден, меняем его на изображения по порядку
                If .Found Then
                    ' Рэндж-старт
                    wdRange.Start = wdRange.Start
                    
                    ' Вставляем знак абзаца в начале
                    wdRange.InsertParagraphBefore
                    
                    ' Вставляем PNG
                    Set shape = doc.InlineShapes.AddPicture(fileToInsert, LinkToFile:=False, SaveWithDocument:=True, Range:=wdRange)
                                                       
                    ' Вставляем знак абзаца в конце
                    wdRange.Collapse Direction:=wdCollapseEnd
                    ' wdRange.InsertParagraphAfter
                End If
            End With
        End If
        fileName = Dir()
    Loop
    
    ' Delete the placeholder text
    Call Delete_SC_PLOTNOST_Placeholder
    
    ' Clean up
    Set wdRange = Nothing
    Set regex = Nothing
    Set doc = Nothing
End Sub

Private Sub Delete_SC_PLOTNOST_Placeholder()
    Dim wdRange As Range
    Dim doc As Document
    Set doc = ActiveDocument
    
    ' Define the text to find and delete
    Dim searchTerm As String
    searchTerm = "[[SC_PLOTNOST]]"
    
    ' Set the range to the entire content of the document
    Set wdRange = doc.Content
    
    ' Use the Find object to locate and delete all instances of the placeholder
    With wdRange.Find
        .text = searchTerm
        .Replacement.text = ""
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
        .MatchWholeWord = False
        .MatchWildcards = False
        .MatchSoundsLike = False
        .MatchAllWordForms = False
        
        ' Execute the find and replace action
        .Execute Replace:=wdReplaceAll
    End With
    
    ' Clean up
    Set wdRange = Nothing
    Set doc = Nothing
End Sub

Sub Insert_SC_PLOTNOST_Placeholder()
    Dim placeholderText As String
    placeholderText = "[[SC_PLOTNOST]]"
    
    ' Insert the placeholder text at the current cursor position
    Selection.TypeText text:=placeholderText
End Sub


Sub InsertPNGdeff()
    Dim wdRange As Range
    Dim shape As InlineShape
    Dim folderPath As String
    Dim fileName As String
    Dim searchPattern As String
    Dim userInput As String
    Dim regex As Object
    Dim doc As Document
    Set regex = CreateObject("VBScript.RegExp")
    
    ' Просим пользователя ввести ID сценария
    userInput = InputBox("Введите ID сценария:")
    
    ' Путь к PNG тот же, что и к DOCX, в котором выполняется скрипт
    folderPath = ActiveDocument.Path & "\"
    Set doc = ActiveDocument
    
    ' Определяем паттерн имени
    searchPattern = "^deff_" & userInput & "_plot\.png$"
    
    ' Регексим
    With regex
        .Global = False
        .IgnoreCase = True
        .pattern = searchPattern
    End With
    
    ' Проходимося по файлам в папке
    fileName = Dir(folderPath & "*.png")
    Do While fileName <> ""
        If regex.Test(fileName) Then
            ' Находим файл, который удовлетворяет паттерну имени
            Dim fileToInsert As String
            fileToInsert = folderPath & fileName

            ' Находим плейсхолдер
            Set wdRange = doc.Content
            With wdRange.Find
                .text = "[[SC_DEFF]]"
                .Forward = True
                .Wrap = wdFindStop
                .Format = False
                .Execute

                ' Если плейсхолдер найден, меняем его на изображения по порядку
                If .Found Then
                    ' Рэндж-старт
                    wdRange.Start = wdRange.Start
                    
                    ' Вставляем знак абзаца в начале
                    wdRange.InsertParagraphBefore
                    
                    ' Вставляем PNG
                    Set shape = doc.InlineShapes.AddPicture(fileToInsert, LinkToFile:=False, SaveWithDocument:=True, Range:=wdRange)
                                                       
                    ' Вставляем знак абзаца в конце
                    wdRange.Collapse Direction:=wdCollapseEnd
                    ' wdRange.InsertParagraphAfter
                End If
            End With
        End If
        fileName = Dir()
    Loop
    
    ' Delete the placeholder text
    Call Delete_SC_DEFF_Placeholder
    
    ' Clean up
    Set wdRange = Nothing
    Set regex = Nothing
    Set doc = Nothing
End Sub

Private Sub Delete_SC_DEFF_Placeholder()
    Dim wdRange As Range
    Dim doc As Document
    Set doc = ActiveDocument
    
    ' Define the text to find and delete
    Dim searchTerm As String
    searchTerm = "[[SC_DEFF]]"
    
    ' Set the range to the entire content of the document
    Set wdRange = doc.Content
    
    ' Use the Find object to locate and delete all instances of the placeholder
    With wdRange.Find
        .text = searchTerm
        .Replacement.text = ""
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
        .MatchWholeWord = False
        .MatchWildcards = False
        .MatchSoundsLike = False
        .MatchAllWordForms = False
        
        ' Execute the find and replace action
        .Execute Replace:=wdReplaceAll
    End With
    
    ' Clean up
    Set wdRange = Nothing
    Set doc = Nothing
End Sub

Sub Insert_SC_DEFF_Placeholder()
    Dim placeholderText As String
    placeholderText = "[[SC_DEFF]]"
    
    ' Insert the placeholder text at the current cursor position
    Selection.TypeText text:=placeholderText
End Sub


Sub InsertPNGhrrp()
    Dim wdRange As Range
    Dim shape As InlineShape
    Dim folderPath As String
    Dim fileName As String
    Dim searchPattern As String
    Dim userInput As String
    Dim regex As Object
    Dim doc As Document
    Set regex = CreateObject("VBScript.RegExp")
    
    ' Просим пользователя ввести ID сценария
    userInput = InputBox("Введите ID сценария:")
    
    ' Путь к PNG тот же, что и к DOCX, в котором выполняется скрипт
    folderPath = ActiveDocument.Path & "\"
    Set doc = ActiveDocument
    
    ' Определяем паттерн имени
    searchPattern = "^hrrp_" & userInput & "_plot\.png$"
    
    ' Регексим
    With regex
        .Global = False
        .IgnoreCase = True
        .pattern = searchPattern
    End With
    
    ' Проходимося по файлам в папке
    fileName = Dir(folderPath & "*.png")
    Do While fileName <> ""
        If regex.Test(fileName) Then
            ' Находим файл, который удовлетворяет паттерну имени
            Dim fileToInsert As String
            fileToInsert = folderPath & fileName

            ' Находим плейсхолдер
            Set wdRange = doc.Content
            With wdRange.Find
                .text = "[[SC_HRRP]]"
                .Forward = True
                .Wrap = wdFindStop
                .Format = False
                .Execute

                ' Если плейсхолдер найден, меняем его на изображения по порядку
                If .Found Then
                    ' Рэндж-старт
                    wdRange.Start = wdRange.Start
                    
                    ' Вставляем знак абзаца в начале
                    wdRange.InsertParagraphBefore
                    
                    ' Вставляем PNG
                    Set shape = doc.InlineShapes.AddPicture(fileToInsert, LinkToFile:=False, SaveWithDocument:=True, Range:=wdRange)
                                                       
                    ' Вставляем знак абзаца в конце
                    wdRange.Collapse Direction:=wdCollapseEnd
                    ' wdRange.InsertParagraphAfter
                End If
            End With
        End If
        fileName = Dir()
    Loop
    
    ' Delete the placeholder text
    Call Delete_SC_HRRP_Placeholder
    
    ' Clean up
    Set wdRange = Nothing
    Set regex = Nothing
    Set doc = Nothing
End Sub

Private Sub Delete_SC_HRRP_Placeholder()
    Dim wdRange As Range
    Dim doc As Document
    Set doc = ActiveDocument
    
    ' Define the text to find and delete
    Dim searchTerm As String
    searchTerm = "[[SC_HRRP]]"
    
    ' Set the range to the entire content of the document
    Set wdRange = doc.Content
    
    ' Use the Find object to locate and delete all instances of the placeholder
    With wdRange.Find
        .text = searchTerm
        .Replacement.text = ""
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
        .MatchWholeWord = False
        .MatchWildcards = False
        .MatchSoundsLike = False
        .MatchAllWordForms = False
        
        ' Execute the find and replace action
        .Execute Replace:=wdReplaceAll
    End With
    
    ' Clean up
    Set wdRange = Nothing
    Set doc = Nothing
End Sub

Sub Insert_SC_HRRP_Placeholder()
    Dim placeholderText As String
    placeholderText = "[[SC_HRRP]]"
    
    ' Insert the placeholder text at the current cursor position
    Selection.TypeText text:=placeholderText
End Sub
