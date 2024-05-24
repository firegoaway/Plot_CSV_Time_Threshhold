#NoEnv
#SingleInstance, Force
; #Include GetSelectedFile.ahk

Gui, Add, Text, x12 y19 w170 h40 +Center, Выберите параметр`, воздействующий на ИП ДОТ:
Gui, Add, DropDownList, x12 y69 w170 h60 vQuantity, VISIBILITY|EXTINCTION COEFFICIENT|OPTICAL DENSITY
Gui, Add, Text, x12 y109 w170 h40 +Center, Введите высоту помещения`, в котором требуется определить tпор:
Gui, Add, Edit, x62 y159 w90 h20 vHZ
Gui, Add, Button, x12 y209 w170 h30 gOkButton, OK
Gui, Add, Text, x12 y159 w40 h20 , Hпом =
Gui, Add, Text, x162 y159 w20 h20 , м

Gui, Show, x732 y442 h265 w200, Isert_Devc_v0.2.1
Return

OkButton:
    Gui, Submit, NoHide
    if (Quantity = "")
    {
        MsgBox, % "Значение параметра, воздействующего на ИП ДОТ, не может быть пустым."
        Return ; Return to allow further actions without exiting the program
    }
    IniWrite, %Quantity%, %A_ScriptDir%\IniQuantity.ini, IniQuantity, Quantity
    if (HZ = "") || (HZ <= 0)
    {
        MsgBox, % "Введите достоверное значение высоты."
        Return ; Return to allow further actions without exiting the program
    }
    IniWrite, %HZ%, %A_ScriptDir%\IniHZ.ini, IniHZ, HZ
    ; MsgBox, % "Параметр: " . Quantity . "`nВысота: " . HZ
    Gui, Hide

    ; Назначаем файлы ввода и вывода
    IniRead, filePath, %A_ScriptDir%\filePath.ini, filePath, filePath

    folderPath := RegExReplace(filePath, "(.*\\).*", "$1")
        folderPath := SubStr(folderPath, 1, StrLen(folderPath) - 1)
    fileName := RegExReplace(filePath, ".+\\(.+)$", "$1")
        fileName := SubStr(fileName, 1, StrLen(fileName) - 4)

    inputFile := filePath
    outputFile := folderPath "\" fileName "_tout.fds"
    ; MsgBox, % "inputFile is " inputFile "`noutputFile is " outputFile

    ; Читаем .fds
    FileRead, fdsContents, %inputFile%

    ; Делим .fds построчно
    StringSplit, lines, fdsContents, `n

    newContents := ""
    meshIndex := 0
    inMeshSection := false

    if (Quantity = "VISIBILITY")
    {
        setpoint := 28.5709
        trip_direction := -1
        IniWrite, %setpoint%, %A_ScriptDir%\IniSetpoint.ini, IniSetpoint, setpoint
    }
    else if (Quantity = "EXTINCTION COEFFICIENT")
    {
        setpoint := 0.2
        trip_direction := 1
        IniWrite, %setpoint%, %A_ScriptDir%\IniSetpoint.ini, IniSetpoint, setpoint
    }
    else if (Quantity = "OPTICAL DENSITY")
    {
        setpoint := 0.023
        trip_direction := 1
        IniWrite, %setpoint%, %A_ScriptDir%\IniSetpoint.ini, IniSetpoint, setpoint
    }

    loop, %lines0%
    {
        line := Trim(lines%A_Index%)
        
        if InStr(line, "&HEAD") && InStr(line, "CHID=")
        {
            ; Extract the CHID value and append _tout
            line := RegExReplace(line, "CHID='([^']*)'", "CHID='`$1_tout'")
        }

        if InStr(line, "&MESH")
        {
            meshIndex++
            inMeshSection := true
            
            if RegExMatch(line, "IJK=(\d+),(\d+),(\d+).*?XB=([\d\.-]+),([\d\.-]+),([\d\.-]+),([\d\.-]+),([\d\.-]+),([\d\.-]+)", match)
            {
                I := match1
                J := match2
                K := match3
                X1 := match4, X2 := match5
                Y1 := match6, Y2 := match7
                Z1 := match8, Z2 := match9
                
                deltaX := (X2 - X1) / I
                deltaY := (Y2 - Y1) / J
                deltaZ := (Z2 - Z1) / K
                
                Z := HZ - deltaZ
                
                Loop, % I
                {
                    xIndex := A_Index - 1
                    X := X1 + xIndex * deltaX
                    Loop, % J
                    {
                        yIndex := A_Index
                        Y := Y1 + (yIndex - 2) * deltaY
                        
                        actualX := Round(X + deltaX, 2)
                        actualY := Round(Y + deltaY, 2)
                        
                        devcline := "&DEVC ID='DEVC_X" (xIndex + 1) "Y" yIndex "_MESH_" meshIndex "' QUANTITY='" Quantity "' XYZ=" actualX "," actualY "," Z ", " "SETPOINT=" setpoint ", " "TRIP_DIRECTION=" trip_direction "/`n"
                        
                        newContents .= devcline
                    }
                }
            }
        }
        newContents .= line . "`n"
    }
    IniWrite, %deltaZ%, %A_ScriptDir%\InideltaZ.ini, InideltaZ, deltaZ
    
    FileAppend, %newContents%, %outputFile%
    ; MsgBox, Успешно! Новый файл создан: %outputFile%
    
    ExitApp
Return

GuiClose:
    ExitApp
Return
