Attribute VB_Name = "Module4"
Sub ExportChartsAsImages()
    Dim ws As Worksheet
    Dim chtObj As ChartObject
    Dim folderPath As String
    Dim fileName As String
    Dim userFolder As FileDialog
    Dim i As Integer
    Dim tempWorkbook As Workbook
    Dim originalCalculationMode As XlCalculation

    On Error GoTo Cleanup

    ' Turn off screen updating, events, and set calculation to manual
    Application.ScreenUpdating = False
    Application.EnableEvents = False
    originalCalculationMode = Application.Calculation
    Application.Calculation = xlCalculationManual

    ' Set the worksheet to the active one
    Set ws = ActiveSheet

    ' Create a FileDialog object as a folder picker dialog box
    Set userFolder = Application.FileDialog(msoFileDialogFolderPicker)

    ' Prompt the user to select a folder
    With userFolder
        .Title = "Select Folder to Save Images"
        If .Show = -1 Then ' If user pressed OK
            folderPath = .SelectedItems(1)
        Else ' If user pressed Cancel
            MsgBox "Folder selection was cancelled. Exiting."
            GoTo Cleanup
        End If
    End With

    ' Ensure folder path ends with a backslash
    If Right(folderPath, 1) <> "\" Then
        folderPath = folderPath & "\"
    End If

    ' Loop through all chart objects in the active sheet
    i = 1
    For Each chtObj In ws.ChartObjects
        ' If the chart is empty, skip the export
        If chtObj.Chart.SeriesCollection.Count > 0 Then
            ' Create a new temporary workbook
            Set tempWorkbook = Workbooks.Add

            ' Copy the chart object to the temp workbook's first sheet
            chtObj.Chart.ChartArea.Copy

            tempWorkbook.Sheets(1).Paste
            DoEvents

            ' Generate a file name for the image
            fileName = folderPath & "Chart_" & i & ".png"

            ' Export the chart from the temp workbook to a file
            tempWorkbook.Sheets(1).ChartObjects(1).Chart.Export fileName:=fileName

            ' Close and delete the temporary workbook
            tempWorkbook.Close SaveChanges:=False

            ' Increment the filename index
            i = i + 1
        Else
            Debug.Print "Skipped empty chart " & chtObj.Name
        End If
    Next chtObj

    ' Inform the user that the process is complete
    MsgBox "All charts have been exported as images to " & folderPath

Cleanup:
    ' Restore application settings
    Application.ScreenUpdating = True
    Application.EnableEvents = True
    Application.Calculation = originalCalculationMode
End Sub

