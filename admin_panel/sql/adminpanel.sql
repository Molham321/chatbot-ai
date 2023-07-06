INSERT INTO admin_panel_adminsettings (id, modified_at, similarity_factor, context_factor, matching_method,
                                               greeting_text, noanswer_text, mail_timeout_in_seconds,
                                               number_of_quality_test_answers, similarity_mail_threshold,
                                               employee_joined_text, employee_left_text, user_left_text,
                                               mail_request_text, mail_sent_text, mail_input_text,
                                               mail_invalid_input_text, mail_cancel_text)
VALUES (1, '2023-07-01 20:51:34.473114', 1.0000, 1.0000, 'cosine',
        'Hallo ich bin Fachi, der Chatbot der Fachhochschule Erfurt. Wie kann ich dir helfen?',
        'Das habe ich leider nicht verstanden, probier es bitte nochmal.', 60000, 5, 1.4,
        'Ein Mitarbeiter ist der Unterhaltung beigetreten.', 'Der Mitarbeiter hat die Unterhaltung verlassen.',
        'Der Nutzer hat die Unterhaltung beendet.', 'Möchtest du stattdessen eine E-Mail versenden?',
        'Deine E-Mail wurde an einen Mitarbeiter versandt. Wir werden deine Frage schnellstmöglich beantworten.',
        'Bitte gib nun deine E-Mail Adresse sein.', 'Bitte gebe eine gültige E-Mail Adresse ein.',
        'Okay, ich werde keine E-Mail versenden.');