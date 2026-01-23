-- =====================================================
-- SERIENBRIEF E-MAIL SCRIPT FÜR MS WORD + OUTLOOK (MAC)
-- Versendet Serienbriefe per E-Mail mit 2-5 Minuten Verzögerung
-- angepasst für: Salutation, FirstName, LastName, Email
-- =====================================================

-- KONFIGURATION
-- Pfad zur Word-Vorlage mit Seriendruckfeldern
property wordTemplatePath : "/Users/sebastian/Desktop/serienbrief_vorlage.docx"

-- Pfad zur Excel/CSV Datenquelle
property dataSourcePath : "/Users/sebastian/Desktop/empfaenger.xlsx"

-- E-Mail Betreff
property emailSubject : "Ihr personalisierter Betreff"

-- Minimale und maximale Verzögerung in Sekunden (2-5 Minuten)
property minDelay : 120
property maxDelay : 300

-- =====================================================
-- HAUPTPROGRAMM
-- =====================================================

on run
	-- Dialogfenster zur Dateiauswahl
	display dialog "🔵 Word Serienbrief E-Mail Versand" & return & return & ¬
		"Spaltenformat: Salutation, FirstName, LastName, Email" & return & ¬
		"1. Liest Empfänger aus Excel/CSV" & return & ¬
		"2. Erstellt Mails aus Word-Vorlage" & return & ¬
		"3. Sendet mit 2-5 Min. Verzögerung" & return & return & ¬
		"Dateien auswählen?" buttons {"Abbrechen", "Dateien auswählen"} default button 2 cancel button 1
	
	-- Word-Vorlage auswählen
	set wordFile to choose file with prompt "Wählen Sie die Word-Vorlage (.docx):" of type {"com.microsoft.word.document.macroenabled", "org.openxmlformats.wordprocessingml.document"}
	set wordTemplatePath to POSIX path of wordFile
	
	-- Datenquelle auswählen
	set dataFile to choose file with prompt "Wählen Sie die Datenquelle (Excel oder CSV):" of type {"public.comma-separated-values-text", "org.openxmlformats.spreadsheetml.sheet", "com.microsoft.excel.xls"}
	set dataSourcePath to POSIX path of dataFile
	
	-- Betreff eingeben
	set subjectInput to display dialog "E-Mail Betreff eingeben:" default answer emailSubject
	set emailSubject to text returned of subjectInput
	
	-- Empfänger aus Datenquelle laden
	set recipients to my loadRecipientsFromFile(dataSourcePath)
	set totalRecipients to count of recipients
	
	if totalRecipients = 0 then
		display dialog "❌ Keine Empfänger gefunden." buttons {"OK"} default button 1
		return
	end if
	
	-- Bestätigung
	display dialog "📧 Bereit zum Versand" & return & return & ¬
		"Empfänger: " & totalRecipients & return & ¬
		"Verzögerung: 2-5 Minuten" & return & return & ¬
		"Starten?" buttons {"Abbrechen", "Senden"} default button 2 cancel button 1
	
	-- Sende-Schleife
	set sentCount to 0
	set failedList to {}
	
	repeat with i from 1 to totalRecipients
		set currentRecipient to item i of recipients
		set recipientEmail to email of currentRecipient
		
		try
			-- Word-Dokument erstellen
			set emailContent to my createMailMergeContent(wordTemplatePath, currentRecipient)
			
			-- Senden
			my sendEmailViaOutlook(recipientEmail, emailSubject, emailContent)
			set sentCount to sentCount + 1
			
			display notification "Gesendet: " & recipientEmail with title "Mail " & i & "/" & totalRecipients
			
		on error errMsg
			set end of failedList to {recipientEmail, errMsg}
		end try
		
		-- Warten (außer beim Letzten)
		if i < totalRecipients then
			set waitTime to my getRandomDelay(minDelay, maxDelay)
			display notification "Nächste Mail in " & (round (waitTime / 60)) & " Min."
			delay waitTime
		end if
	end repeat
	
	-- Abschluss
	display dialog "Fertig! Gesendet: " & sentCount & ", Fehler: " & (count of failedList) buttons {"OK"} default button 1
end run

-- =====================================================
-- DATEN IMPORT
-- =====================================================

on loadRecipientsFromFile(filePath)
	if filePath ends with ".csv" then
		return my loadFromCSV(filePath)
	else
		return my loadFromExcel(filePath)
	end if
end loadRecipientsFromFile

on loadFromCSV(csvPath)
	set recipients to {}
	set csvContent to read POSIX file csvPath as «class utf8»
	set csvLines to paragraphs of csvContent
	
	-- Erwarte Spalten: Salutation, FirstName, LastName, Email
	repeat with i from 2 to count of csvLines -- Header überspringen
		set lineStr to item i of csvLines
		if lineStr is not "" then
			set AppleScript's text item delimiters to ","
			set fields to text items of lineStr
			set AppleScript's text item delimiters to ""
			
			-- Index 4 = Email
			if (count of fields) ≥ 4 then
				set rec to {salutation:item 1 of fields, firstname:item 2 of fields, lastname:item 3 of fields, email:item 4 of fields}
				set end of recipients to rec
			end if
		end if
	end repeat
	return recipients
end loadFromCSV

on loadFromExcel(excelPath)
	set recipients to {}
	tell application "Microsoft Excel"
		open POSIX file excelPath
		set lastRow to (first row index of (get end (cell "A1") direction toward the bottom)) - 1
		
		repeat with rowNum from 2 to lastRow
			-- Spalte A=Salutation, B=FirstName, C=LastName, D=Email
			set sVal to string value of cell ("A" & rowNum)
			set fVal to string value of cell ("B" & rowNum)
			set lVal to string value of cell ("C" & rowNum)
			set eVal to string value of cell ("D" & rowNum)
			
			if eVal is not "" then
				set end of recipients to {salutation:sVal, firstname:fVal, lastname:lVal, email:eVal}
			end if
		end repeat
		close active workbook saving no
	end tell
	return recipients
end loadFromExcel

-- =====================================================
-- WORD VERARBEITUNG
-- =====================================================

on createMailMergeContent(templatePath, recipData)
	set emailContent to ""
	tell application "Microsoft Word"
		open POSIX file templatePath
		set docContent to content of text object of active document
		
		-- Platzhalter ersetzen
		-- Unterstützt «Placeholder» und {{Placeholder}}
		set docContent to my replaceText(docContent, "«Salutation»", salutation of recipData)
		set docContent to my replaceText(docContent, "«FirstName»", firstname of recipData)
		set docContent to my replaceText(docContent, "«LastName»", lastname of recipData)
		set docContent to my replaceText(docContent, "«Email»", email of recipData)
		
		set docContent to my replaceText(docContent, "{{Salutation}}", salutation of recipData)
		set docContent to my replaceText(docContent, "{{FirstName}}", firstname of recipData)
		set docContent to my replaceText(docContent, "{{LastName}}", lastname of recipData)
		set docContent to my replaceText(docContent, "{{Email}}", email of recipData)
		
		set emailContent to docContent
		close active document saving no
	end tell
	return emailContent
end createMailMergeContent

-- =====================================================
-- OUTLOOK & UTILS
-- =====================================================

on sendEmailViaOutlook(toAddr, subj, body)
	tell application "Microsoft Outlook"
		set newMsg to make new outgoing message with properties {subject:subj, content:body}
		make new to recipient at newMsg with properties {email address:{address:toAddr}}
		send newMsg
	end tell
end sendEmailViaOutlook

on replaceText(str, find, rep)
	set AppleScript's text item delimiters to find
	set itemsList to text items of str
	set AppleScript's text item delimiters to rep
	set res to itemsList as text
	set AppleScript's text item delimiters to ""
	return res
end replaceText

on getRandomDelay(minS, maxS)
	return minS + (random number from 0 to (maxS - minS))
end getRandomDelay
