from firebase_admin import credentials
from firebase_admin import firestore

db = firestore.client()
EMAIL_COLLECTION = "mail" 


def enviar_email_reset(destinatario, codigo):
    assunto = "Seu Código de Redefinição de Senha - Move Hive"

    corpo_html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap" rel="stylesheet">
    </head>
    <body style="margin: 0; padding: 0; background-color: #f0f2f5; font-family: Arial, sans-serif;">
        <table border="0" cellpadding="0" cellspacing="0" width="100%">
            <tr>
                <td style="padding: 20px 0;">
                    <table align="center" border="0" cellpadding="0" cellspacing="0" width="600" style="border-collapse: collapse; background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);">
                        <!-- LOGO -->
                        <tr>
                            <td align="center" style="padding: 40px 0 20px 0;">
                                <span style="font-family: 'Montserrat', sans-serif; font-size: 3.5em; font-weight: bold; color: #1e1e1e; display: block; line-height: 1; margin-bottom: -5px;">MOVE</span>
                                <span style="font-family: 'Montserrat', sans-serif; font-size: 3.5em; font-weight: bold; color: #facc15; display: block; line-height: 1;">HIVE</span>
                            </td>
                        </tr>
                        <!-- TÍTULO -->
                        <tr>
                            <td align="center" style="padding: 0 30px 20px 30px; font-size: 24px; color: #333333; font-family: Arial, sans-serif;">
                                Seu código de verificação
                            </td>
                        </tr>
                        <!-- CAIXA DO CÓDIGO -->
                        <tr>
                            <td style="padding: 0 30px 30px 30px;">
                                <div style="background-color: #2c2c2c; border-radius: 8px; padding: 20px 0; text-align: center;">
                                    <span style="color: #ffffff; font-size: 36px; font-weight: bold; letter-spacing: 10px; font-family: 'Courier New', Courier, monospace;">
                                        {codigo}
                                    </span>
                                </div>
                            </td>
                        </tr>
                        <!-- TEXTO DE INSTRUÇÃO -->
                        <tr>
                            <td align="center" style="padding: 0 40px 20px 40px; color: #555555; font-size: 16px; line-height: 24px; font-family: Arial, sans-serif;">
                                Copie e cole este código para redefinir sua senha. Se você não solicitou isso, pode ignorar este e-mail com segurança.
                            </td>
                        </tr>
                        <!-- TEXTO DE EXPIRAÇÃO -->
                        <tr>
                            <td align="center" style="padding: 0 30px 40px 30px; color: #888888; font-size: 14px; font-family: Arial, sans-serif;">
                                Este código expira em 10 minutos.
                            </td>
                        </tr>
                        <!-- RODAPÉ -->
                        <tr>
                           <td align="center" style="padding: 20px 30px; border-top: 1px solid #eeeeee; font-size: 12px; color: #888888; font-family: Arial, sans-serif;">
                                &copy; 2025 Move Hive. Todos os direitos reservados.
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    email_doc = {
        'to': destinatario, 
        'message': {
            'subject': assunto,
            'html': corpo_html 
        }
    }

    try:
        db.collection(EMAIL_COLLECTION).add(email_doc)
        print(f"Documento de e-mail adicionado ao Firestore para {destinatario}. Extensão irá disparar o envio.")
    except Exception as e:
        print(f"Falha ao adicionar documento de e-mail ao Firestore para {destinatario}. Erro: {e}")
        raise e