Attribute VB_Name = "Module2"
Sub AnalyzeAndHighlight()
    Dim ws As Worksheet
    Dim col As Range
    Dim cell As Range
    Dim rowNum As Long
    Dim exceedColCount As Long
    Dim rowExceed116Index As Long
    Dim cellCount As Long
    Dim lastCol As Long
    Dim lastRow As Long
    Dim i As Long, j As Long
    Dim Cc As Long, Cs As Double, H As Double, R As Long, L As Double, deff As Double, F As Long
    Dim Pi As Double

    'Specify which worksheet you want to work with
    'Set ws = ThisWorkbook.Worksheets("Лист2")
    Set ws = ActiveSheet
    
    'Calculating Cc
    H = Val(InputBox("Hпом - Высота помещения с очагом пожара (м)", "Hпом"))
    If H <= 3.5 Then
        R = 6.4
    ElseIf H > 3.5 And H <= 6 Then
        R = 6.05
    ElseIf H > 6 And H <= 10 Then
        R = 5.7
    Else
        R = 5.35
    End If
    L = R * Sqr(2)
    Cs = Val(InputBox("Cs - размер ячейки расчётной области (м)", "Cs"))
    deff = L
    F = (MultiplyByPi(1) * (deff ^ 2)) / 4
    F = Application.WorksheetFunction.Ceiling_Math(F)
    Cc = F / Cs
    Cc = Application.WorksheetFunction.Ceiling_Math(Cc)
    
    ' Determine the last column and last row with data
    lastCol = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column
    lastRow = ws.Cells(ws.Rows.Count, 1).End(xlUp).row
    
    Dim quantity As String
    Dim qThreshold As Double
    
    quantity = Trim(InputBox("quantity = ", "quantity"))
    qThreshold = Val(InputBox("qThreshold = ", "qThreshold"))
    
    exceedColCount = 0
    
    If quantity = "vis" Then
        For i = 2 To lastCol ' Start from the second column
            For j = 1 To lastRow
                If ws.Cells(j, i).Value <= qThreshold Then
                    exceedColCount = exceedColCount + 1
                    Exit For
                End If
            Next j
        Next i
    ElseIf quantity = "ext" Or quantity = "opt" Then
        For i = 2 To lastCol ' Start from the second column
            For j = 1 To lastRow
                If ws.Cells(j, i).Value >= qThreshold Then
                    exceedColCount = exceedColCount + 1
                    Exit For
                End If
            Next j
        Next i
    End If
    
    rowExceed116Index = 0
    
    If quantity = "vis" Then
        For rowNum = 1 To lastRow
            cellCount = 0
            For i = 2 To lastCol ' Start from the second column
                If ws.Cells(rowNum, i).Value <= qThreshold Then
                    cellCount = cellCount + 1
                End If
            Next i
            If cellCount > Cc Then
                rowExceed116Index = rowNum
                Exit For
            End If
        Next rowNum
    ElseIf quantity = "ext" Or quantity = "opt" Then
        For rowNum = 1 To lastRow
            cellCount = 0
            For i = 2 To lastCol ' Start from the second column
                If ws.Cells(rowNum, i).Value >= qThreshold Then
                    cellCount = cellCount + 1
                End If
            Next i
            If cellCount > Cc Then
                rowExceed116Index = rowNum
                Exit For
            End If
        Next rowNum
    End If

    If rowExceed116Index > 0 Then
        ws.Rows(rowExceed116Index).Font.Bold = True
        ws.Rows(rowExceed116Index).Interior.Color = RGB(255, 255, 0) ' Optional: Add a yellow background
    End If
    
    ' Output results to the Immediate Window (Ctrl+G to view)
    Debug.Print "Number of columns with at least one cell <= 28.5709: " & exceedColCount
    Debug.Print "First row where cells <= 28.5709 exceed 116 cells: " & rowExceed116Index
End Sub

Function MultiplyByPi(inputVal)

Dim Pi As Double

MultiplyByPi = inputVal * Application.WorksheetFunction.Pi()

End Function
