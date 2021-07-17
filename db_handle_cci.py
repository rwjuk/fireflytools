import pymysql.cursors

conn = pymysql.connect(
    host ="tools.db.svc.eqiad.wmflabs",
    user='s53758',
    password='YeQ2uFKXCexU38Oa',
    db = 's53758__ccistats',
    charset='utf8',
    use_unicode=True
)
