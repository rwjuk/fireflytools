#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, datetime, logging
import pywikibot
import toolforge

from db_handle import *

site = pywikibot.Site()

tf_conn = toolforge.connect("enwiki")

def task_permitted(task_num):
    shutoff_page_title = "User:FireflyBot_II/shutoff/{}".format(task_num)
    shutoff_page = pywikibot.Page(site, shutoff_page_title)

    return (shutoff_page.get().strip().lower() == "active")

def get_pages_with_pending_revs():
        cur = tf_conn.cursor()
        cur.execute("select page_id,fpp_rev_id from flaggedpage_pending inner join revision on rev_id=fpp_rev_id inner join page on rev_page=page_id")
        return cur.fetchall()

def get_auto_acceptable_revs(page_id, last_accepted_rev):
        cur = tf_conn.cursor()
        acceptable_revs = []
        while last_accepted_rev is not None:
                exec_result = cur.execute("select rev_id from revision inner join actor on rev_actor=actor_id inner join user on user_id=actor_user left join user_groups on ug_user=user_id where (ug_group='extendedconfirmed' or ug_group='confirmed' or ug_group='autoconfirmed' or ug_group='sysop'or ug_group='bot') and rev_parent_id={} and rev_page={}".format(last_accepted_rev, page_id))
                last_accepted_rev = cur.fetchone()[0] if (exec_result > 0) else None
                if last_accepted_rev is not None:
                        if rev_previously_processed(last_accepted_rev):
                                last_accepted_rev = None
                        else:
                                acceptable_revs.append(last_accepted_rev)
        return acceptable_revs

def rev_previously_processed(rev_id):
        cur = conn.cursor()
        return (cur.execute("select rev_id from reviewed_revs where rev_id={}".format(rev_id)) == 1)

def log_revs_as_processed(page_id, last_accepted_rev):
        cur = conn.cursor()
        tf_cur = tf_conn.cursor()
        tf_cur.execute("select rev_id from revision where rev_page='{}' and rev_id>{}".format(page_id, int(last_accepted_rev)))
        for rev_id in [x[0] for x in tf_cur.fetchall()]:
                cur.execute("insert ignore into reviewed_revs (rev_id) values('{}');".format(rev_id))
        conn.commit()

def accept_revision(rev_id):
        csrf = site.get_tokens(["csrf"])['csrf']
        accept_request = pywikibot.data.api.Request(site=site, parameters={'action':'review', 'revid':rev_id, 'comment':'(BOT in trial) Revision should have automatically been accepted as user meets auto-accept threshold. See [[phab:T233561]]', 'token':csrf})
        return accept_request.submit()['review']

def dump_acceptable_rev_onwiki(rev_id):
        p = pywikibot.Page(site, "User:FireflyBot_II/brfa_pc_log")
        old_text = p.get()
        if str(rev_id) not in old_text:
                new_text = "*{0} - accepting [[Special:Diff/{1}|{1}]]\n{2}".format(datetime.datetime.now(), rev_id, old_text)
                p.put(new_text, summary="Logging acceptance of rev {}".format(rev_id), minor=False)

def process_buggy_revs():
        for page_id,last_accepted_rev_id in get_pages_with_pending_revs():
                aa_revs = get_auto_acceptable_revs(page_id, last_accepted_rev_id)
                for aa_rev in aa_revs:
                        result = accept_revision(aa_rev)
                        dump_acceptable_rev_onwiki(aa_rev)
                log_revs_as_processed(page_id, last_accepted_rev_id)

def main(*args):
    logger = logging.getLogger('pcr_bug_bot')
    logger.setLevel(logging.DEBUG)
    trfh = logging.handlers.TimedRotatingFileHandler('logs/pcr_bug_bot', when='D', interval = 3, backupCount = 90)
    trfh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    trfh.setFormatter(formatter)
    logger.addHandler(trfh)
    trfh.doRollover()

    if (task_permitted(1)):
        process_buggy_revs()
    else:
        logger.info(u"Task not permitted to run - onwiki shutoff bit flipped")

if __name__ == "__main__":
    main()
