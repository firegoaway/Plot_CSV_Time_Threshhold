Attribute VB_Name = "Module1"
Sub DeleteColumnsWithOnly30s()
    Dim ws As Worksheet
    Dim col As Range
    Dim cell As Range
    Dim delCol As Boolean
    Dim lastCol As Long
    Dim lastRow As Long
    Dim i As Long
    
    ' Specify which worksheet you want to work with
    ' Set ws = ThisWorkbook.Worksheets("Лист2")
    Set ws = ActiveSheet
    
    ' Determine the last column with data
    lastCol = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column
    lastRow = ws.Cells(ws.Rows.Count, 1).End(xlUp).row
    
    ' Loop through columns from right to left to prevent shifting issues
    Dim quantity As String
    Dim qThreshold As Double
  
    quantity = Trim(InputBox("quantity = ", "quantity"))
    qThreshold = Val(InputBox("qThreshold = ", "qThreshold"))
    
    If quantity = "vis" Then
        For i = lastCol To 1 Step -1
            delCol = True
            For Each cell In ws.Range(ws.Cells(1, i), ws.Cells(lastRow, i))
                If cell.Value < qThreshold Then
                    delCol = False
                    Exit For
                End If
            Next cell
            
            ' Delete the column if all values are > qThreshold
            If delCol Then
                ws.Columns(i).Delete
            End If
        Next i
    ElseIf quantity = "ext" Or quantity = "opt" Then
        For i = lastCol To 1 Step -1
            delCol = True
            For Each cell In ws.Range(ws.Cells(1, i), ws.Cells(lastRow, i))
                If cell.Value > qThreshold Then
                    delCol = False
                    Exit For
                End If
            Next cell
            
            ' Delete the column if all values are < qThreshold
            If delCol Then
                ws.Columns(i).Delete
            End If
        Next i
    End If
End Sub

