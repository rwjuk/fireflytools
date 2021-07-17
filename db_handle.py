import pymysql.cursors

conn = pymysql.connect(
    host ="tools.db.svc.eqiad.wmflabs",
    user='s53758',
    password='YeQ2uFKXCexU38Oa',
    db = 's53758__vpndb',
    charset='utf8',
    use_unicode=True
)
