import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from venv import logger

def enviar_email_reset(destinatario, codigo):
    """
    Envia um e-mail de redefinição de senha com um template HTML profissional.
    """
    remetente = os.getenv("EMAIL_USER")
    senha = os.getenv("EMAIL_PASS")
    assunto = "Seu Código de Redefinição de Senha - Move Hive"

    # --- 1. Crie o corpo de Texto Simples (Fallback) ---
    corpo_texto = f"""
    Olá,
    
    Seu código para redefinir a senha no Move Hive é: {codigo}
    
    Este código expira em 10 minutos.
    
    Se você não solicitou esta redefinição, por favor, ignore este e-mail.
    
    Atenciosamente,
    Equipe Move Hive
    """

    # --- 2. Crie o corpo em HTML usando o template ---
    # O ideal é carregar de um arquivo, mas para simplificar, vamos usar uma f-string.
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
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = assunto
    msg['From'] = f"Move Hive <{remetente}>" 
    msg['To'] = destinatario

    part1 = MIMEText(corpo_texto, 'plain', 'utf-8')
    part2 = MIMEText(corpo_html, 'html', 'utf-8')
    msg.attach(part1)
    msg.attach(part2)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(remetente, senha)
            server.sendmail(remetente, destinatario, msg.as_string())
            logger.info(f"E-mail de reset enviado com sucesso para {destinatario}")
    except Exception as e:
        logger.error(f"Falha ao enviar e-mail de reset para {destinatario}. Erro: {e}")
        raise e