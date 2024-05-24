Attribute VB_Name = "Module3"
Sub ProcessCSV()
    ' Convert CSV to Excel format
    Dim csvFile As Variant
    csvFile = Application.GetOpenFilename("CSV Files (*.csv), *.csv")
    If csvFile = False Then Exit Sub

    Workbooks.Open csvFile
    ActiveWorkbook.SaveAs Replace(csvFile, ".csv", ".xlsx"), xlOpenXMLWorkbook
    Application.DisplayAlerts = False
    ActiveWorkbook.Close

    ' Open the converted Excel file
    Dim excelFile As String
    excelFile = Replace(csvFile, ".csv", ".xlsx")
    Workbooks.Open excelFile

    Dim ws As Worksheet
    Set ws = ActiveSheet
    
    Rows(1).Delete
    
    ' Remove spaces and format cells
    Call RemoveSpacesAndFormat(ws)
    
    ' Delete columns not matching the pattern
    Dim col As Long, lastCol As Long
    Dim R As Long, lastRow As Long
    lastCol = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column
    Dim regex As Object
    Set regex = CreateObject("VBScript.RegExp")
    regex.Pattern = "DEVC_X\d+Y\d+_MESH_\d+"
    
    For col = lastCol To 2 Step -1
        If Not regex.Test(ws.Cells(1, col).Value) Then
            ws.Columns(col).Delete
        End If
    Next col

    ' Delete columns with cells all >= 30
    lastCol = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column
    lastRow = ws.Cells(ws.Rows.Count, 1).End(xlUp).row
    
    For col = lastCol To 2 Step -1
        Dim deleteCol As Boolean
        deleteCol = True
        For R = 2 To lastRow
            If ws.Cells(R, col).Value < 30 Then
                deleteCol = False
                Exit For
            End If
        Next R
        If deleteCol Then ws.Columns(col).Delete
    Next col
    
    ' Count columns with values <= 28.5709
    lastCol = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column
    Dim colCount As Long
    colCount = 0
    
    For col = 2 To lastCol
        For R = 2 To lastRow
            If ws.Cells(R, col).Value <= 28.5709 Then
                colCount = colCount + 1
                Exit For
            End If
        Next R
    Next col

    MsgBox "Number of columns (except the first one) with at least one cell with value <= 28.5709: " & colCount
    
    ' Highlight a single row with more than calculated cells value <= 28.5709
    Dim Cc As Double, Cs As Double, H As Double, Radius As Double, L As Double, deff As Double, F As Double
    Dim Pi As Double
    
    H = Val(InputBox("H = ", "columnNumber"))
    If H <= 3.5 Then
        Radius = 6.4
    ElseIf H > 3.5 And H <= 6 Then
        Radius = 6.05
    ElseIf H > 6 And H <= 10 Then
        Radius = 5.7
    Else
        Radius = 5.35
    End If

    L = Radius * Sqr(2)
    MsgBox "L = " & L
    Cs = Val(InputBox("Cs = ", "columnNumber"))
    deff = L
    F = (MultiplyByPi(1) * (deff ^ 2)) / 4
    ' MsgBox "F = " & F
    F = Application.WorksheetFunction.Ceiling_Math(F)
    MsgBox "F = " & F
    Cc = F / Cs
    MsgBox "Cc = " & Cc
    
    Dim highlighted As Boolean
    highlighted = False
    Dim highlightedCols As Collection
    Set highlightedCols = New Collection
    
    For R = 2 To lastRow
        Dim cellCount As Long
        cellCount = 0
        For col = 2 To lastCol
            If ws.Cells(R, col).Value <= 28.5709 Then
                cellCount = cellCount + 1
            End If
        Next col
        If cellCount >= Cc And Not highlighted Then
            For col = 2 To lastCol
                If ws.Cells(R, col).Value <= 28.5709 Then
                    ' Highlight the cell
                    With ws.Cells(R, col)
                        .Font.Bold = True
                        .Interior.Color = RGB(144, 238, 144) ' Light green background
                        .Borders(xlEdgeLeft).LineStyle = xlContinuous
                        .Borders(xlEdgeTop).LineStyle = xlContinuous
                        .Borders(xlEdgeBottom).LineStyle = xlContinuous
                        .Borders(xlEdgeRight).LineStyle = xlContinuous
                    End With
                    highlightedCols.Add col
                    With ws.Cells(R, 1)
                        .Font.Bold = True
                        .Interior.Color = RGB(255, 0, 0) ' Light red background
                        .Borders(xlEdgeLeft).LineStyle = xlContinuous
                        .Borders(xlEdgeTop).LineStyle = xlContinuous
                        .Borders(xlEdgeBottom).LineStyle = xlContinuous
                        .Borders(xlEdgeRight).LineStyle = xlContinuous
                    End With
                    highlightedCols.Add col
                End If
            Next col
            highlighted = True
        End If
    Next R
    
    ' Plot graphs for highlighted columns against the first column
    Call PlotGraphs(ws, highlightedCols, lastRow)
    
    Application.DisplayAlerts = True
    MsgBox "Processing Completed"
End Sub

Sub RemoveSpacesAndFormat(ws As Worksheet)
    ws.Cells.NumberFormat = "General"
End Sub

Sub HighlightColumnsWithThreshold(ws As Worksheet, threshold As Double)
    Dim lastRow As Long
    Dim lastCol As Long
    Dim col As Long
    Dim row As Long
    Dim cell As Range
    Dim mean As Double
    Dim highlightCount As Integer
    Dim highlightedRows As Collection
    
    ' Initialize collection to store highlighted rows
    Set highlightedRows = New Collection
    
    ' Find the last row and column in the used range
    lastRow = ws.Cells(ws.Rows.Count, 1).End(xlUp).row
    lastCol = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column

    ' Initialize a collection to store the highlighted columns
    Set highlightedCols = New Collection
    
    ' Loop through each column starting from the second column
    For col = 2 To lastCol
        highlightCount = 0
        
        ' Calculate the mean of values in the column
        mean = Application.WorksheetFunction.Average(ws.Cells(2, col).Resize(lastRow - 1))
        
        ' Loop through each cell in the column
        For row = 2 To lastRow
            Set cell = ws.Cells(row, col)
            
            ' Check if the value is beyond the threshold
            If Abs(cell.Value - mean) > threshold Then
                cell.Interior.Color = RGB(255, 255, 0)  ' Highlight cell in yellow
                
                ' Increment the highlight count
                highlightCount = highlightCount + 1
                
                ' Add the row number to the highlightedRows collection
                If Not InCollection(highlightedRows, row) Then
                    highlightedRows.Add row
                End If
            End If
        Next row
        
        ' If more than 10 cells are highlighted, consider the column highlighted
        If highlightCount > 10 Then
            highlightedCols.Add col
            
            ' Highlight the first cell in each highlighted row with red color, outline it, and make it bold
            For row = 2 To lastRow
                Set cell = ws.Cells(row, col)
                If cell.Interior.Color = RGB(255, 255, 0) Then
                    With ws.Cells(row, 1)
                        .Interior.Color = RGB(255, 0, 0)  ' Red color
                        .Borders.LineStyle = xlContinuous  ' Outline the cell
                        .Font.Bold = True  ' Make the font bold
                        
                        ' Show a message box with the value in the first cell of the highlighted row
                        MsgBox "Value in the first cell of the highlighted row: " & .Value
                    End With
                End If
            Next row
        End If
    Next col
    
    ' Call HideRowsExceptHighlights to hide all rows except the first one and highlighted rows
    HideRowsExceptHighlights ws, highlightedRows
        
    ' Call PlotGraphs to create charts for the highlighted columns
    Call PlotGraphs(ws, highlightedCols, lastRow)
End Sub

Sub HideRowsExceptHighlights(ws As Worksheet, highlightedRows As Collection)
    Dim lastRow As Long
    Dim row As Long
    Dim i As Long
    Dim isHighlighted As Boolean
    
    ' Find the last row in the used range
    lastRow = ws.Cells(ws.Rows.Count, 1).End(xlUp).row
    
    ' Loop through each row, starting from the second row
    For row = 2 To lastRow
        isHighlighted = False
        
        ' Check if the current row is in the highlightedRows collection
        For i = 1 To highlightedRows.Count
            If highlightedRows(i) = row Then
                isHighlighted = True
                Exit For
            End If
        Next i
        
        ' Hide the row if it's not highlighted
        If Not isHighlighted Then
            ws.Rows(row).Hidden = True
        End If
    Next row
End Sub

Sub PlotGraphs(ws As Worksheet, highlightedCols As Collection, lastRow As Long)
    Dim col As Variant
    Dim chartObj As ChartObject
    Dim chartRange As Range
    Dim xValuesRange As Range
    Dim chartSheet As Worksheet
    Dim chartTop As Long

    ' Create a new sheet for charts
    On Error Resume Next ' In case the sheet already exists
    Set chartSheet = Worksheets("Highlighted Columns Charts")
    If chartSheet Is Nothing Then
        Set chartSheet = Worksheets.Add
        chartSheet.Name = "Highlighted Columns Charts"
    Else
        chartSheet.Cells.Clear ' Clear existing content if the sheet already exists
    End If
    On Error GoTo 0

    ' Define range of the first column as the X values
    Set xValuesRange = ws.Range(ws.Cells(2, 1), ws.Cells(lastRow, 1))

    chartTop = 10
    For Each col In highlightedCols
        ' Define range of the current highlighted column
        Set chartRange = ws.Range(ws.Cells(2, col), ws.Cells(lastRow, col))  ' Start from the second row to avoid the header

        ' Create a new chart object
        Set chartObj = chartSheet.ChartObjects.Add(Left:=10, Width:=400, Top:=chartTop, Height:=200)
        chartTop = chartTop + 220 ' Adjust the top position for the next chart

        With chartObj.chart
            ' Clear existing data series
            Do While .SeriesCollection.Count > 0
                .SeriesCollection(1).Delete
            Loop

            ' Add a new data series
            .SeriesCollection.NewSeries
            .SeriesCollection(1).XValues = xValuesRange
            .SeriesCollection(1).Values = chartRange

            ' Set chart properties
            .ChartType = xlLine
            .HasTitle = True
            .chartTitle.Text = "Точка " & col & " в области F"
            .Axes(xlCategory).HasTitle = True
            .Axes(xlCategory).AxisTitle.Text = "Время (с)"
            .Axes(xlValue).HasTitle = True
            .Axes(xlValue).AxisTitle.Text = "Значение параметра (м)"

            ' Disable the legend
            .HasLegend = False
        End With
    Next col
End Sub

Function InCollection(col As Collection, key As Variant) As Boolean
    On Error Resume Next
    col (key)
    InCollection = (Err.Number = 0)
    On Error GoTo 0
End Function

Function MultiplyByPi(inputVal)
    MultiplyByPi = inputVal * Application.WorksheetFunction.Pi()
End Function
