-- =====================================================
-- SERIENBRIEF E-MAIL SCRIPT FÜR MICROSOFT OUTLOOK (MAC)
-- Sendet E-Mails mit 2-5 Minuten Verzögerung
-- =====================================================

-- KONFIGURATION: Passen Sie diese Werte an
property emailSubject : "Ihr Betreff hier"
property emailBody : "Sehr geehrte/r {{NAME}},

Ihr E-Mail-Text hier.

{{FIRMA}} wird von uns unterstützt.

Mit freundlichen Grüßen,
Ihr Name"

property senderAccount : "" -- Leer lassen für Standard-Account

-- EMPFÄNGERLISTE: Fügen Sie hier Ihre Empfänger hinzu
-- Format: {email, name, firma}
property recipientList : {¬
	{"max.mustermann@beispiel.de", "Max Mustermann", "Mustermann GmbH"}, ¬
	{"anna.schmidt@firma.de", "Anna Schmidt", "Schmidt AG"}, ¬
	{"peter.mueller@unternehmen.com", "Peter Müller", "Müller & Co."} ¬
}

-- Minimale und maximale Verzögerung in Sekunden (2-5 Minuten = 120-300 Sekunden)
property minDelay : 120
property maxDelay : 300

-- =====================================================
-- HAUPTPROGRAMM
-- =====================================================

on run
	-- Willkommensnachricht
	display dialog "Serienbrief E-Mail Versand" & return & return & ¬
		"Anzahl Empfänger: " & (count of recipientList) & return & ¬
		"Verzögerung: " & (minDelay / 60) & " - " & (maxDelay / 60) & " Minuten" & return & return & ¬
		"Möchten Sie fortfahren?" buttons {"Abbrechen", "Starten"} default button "Starten" cancel button "Abbrechen"
	
	-- Protokoll für gesendete E-Mails
	set sentLog to {}
	set failedLog to {}
	set currentIndex to 1
	set totalEmails to count of recipientList
	
	-- Durch alle Empfänger iterieren
	repeat with recipient in recipientList
		set recipientEmail to item 1 of recipient
		set recipientName to item 2 of recipient
		set recipientFirma to item 3 of recipient
		
		-- E-Mail-Text personalisieren
		set personalizedBody to my replaceText(emailBody, "{{NAME}}", recipientName)
		set personalizedBody to my replaceText(personalizedBody, "{{FIRMA}}", recipientFirma)
		
		-- E-Mail senden
		try
			my sendEmail(recipientEmail, recipientName, emailSubject, personalizedBody)
			set end of sentLog to recipientEmail
			
			-- Fortschritt anzeigen (optional - kann bei großen Mengen auskommentiert werden)
			-- display notification "E-Mail " & currentIndex & "/" & totalEmails & " gesendet an " & recipientName
			
		on error errMsg
			set end of failedLog to {recipientEmail, errMsg}
		end try
		
		-- Warten vor der nächsten E-Mail (außer bei der letzten)
		if currentIndex < totalEmails then
			set randomDelay to my getRandomDelay(minDelay, maxDelay)
			set minutesDelay to (randomDelay / 60)
			
			-- Countdown anzeigen (optional)
			display notification "Nächste E-Mail in " & (round minutesDelay) & " Minuten" with title "Serienbrief"
			
			delay randomDelay
		end if
		
		set currentIndex to currentIndex + 1
	end repeat
	
	-- Abschlussbericht
	set successCount to count of sentLog
	set failCount to count of failedLog
	
	display dialog "Versand abgeschlossen!" & return & return & ¬
		"✅ Erfolgreich gesendet: " & successCount & return & ¬
		"❌ Fehlgeschlagen: " & failCount buttons {"OK"} default button "OK"
	
	-- Falls Fehler aufgetreten sind, Details anzeigen
	if failCount > 0 then
		set errorDetails to ""
		repeat with failedItem in failedLog
			set errorDetails to errorDetails & (item 1 of failedItem) & ": " & (item 2 of failedItem) & return
		end repeat
		display dialog "Fehlgeschlagene E-Mails:" & return & return & errorDetails buttons {"OK"} default button "OK"
	end if
end run

-- =====================================================
-- HILFSFUNKTIONEN
-- =====================================================

-- E-Mail über Outlook senden
on sendEmail(toAddress, toName, subject, body)
	tell application "Microsoft Outlook"
		set newMessage to make new outgoing message with properties {subject:subject, content:body}
		
		-- Empfänger hinzufügen
		make new to recipient at newMessage with properties {email address:{address:toAddress, name:toName}}
		
		-- Optional: CC oder BCC hinzufügen
		-- make new cc recipient at newMessage with properties {email address:{address:"cc@beispiel.de", name:"CC Name"}}
		
		-- E-Mail senden
		send newMessage
	end tell
end sendEmail

-- Text ersetzen
on replaceText(sourceText, findText, replaceWith)
	set AppleScript's text item delimiters to findText
	set textItems to text items of sourceText
	set AppleScript's text item delimiters to replaceWith
	set resultText to textItems as text
	set AppleScript's text item delimiters to ""
	return resultText
end replaceText

-- Zufällige Verzögerung zwischen min und max
on getRandomDelay(minSeconds, maxSeconds)
	return minSeconds + (random number from 0 to (maxSeconds - minSeconds))
end getRandomDelay

-- =====================================================
-- ALTERNATIVE: EMPFÄNGER AUS CSV-DATEI LADEN
-- =====================================================
-- Entkommentieren Sie die folgende Funktion um Empfänger aus einer CSV zu laden

(*
on loadRecipientsFromCSV(csvPath)
    set csvContent to read POSIX file csvPath as «class utf8»
    set csvLines to paragraphs of csvContent
    set loadedRecipients to {}
    
    -- Erste Zeile überspringen (Header)
    repeat with i from 2 to count of csvLines
        set currentLine to item i of csvLines
        if currentLine is not "" then
            set AppleScript's text item delimiters to ","
            set lineItems to text items of currentLine
            set AppleScript's text item delimiters to ""
            
            if (count of lineItems) ≥ 3 then
                set end of loadedRecipients to {item 1 of lineItems, item 2 of lineItems, item 3 of lineItems}
            end if
        end if
    end repeat
    
    return loadedRecipients
end loadRecipientsFromCSV

-- Verwendung:
-- set recipientList to loadRecipientsFromCSV("/Users/IhrName/Desktop/empfaenger.csv")
-- CSV-Format: email,name,firma
*)
