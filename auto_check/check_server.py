from flask import Flask, request, jsonify

from auto_check.AB6 import AB6CheckService
from auto_check.AFZ.AFZCheckService import show_check_all_info, show_check_part_info
from auto_check.A6E.A6ECheckService import A6ECheckService
from auto_check.AQG.AQGCheckService import AQGCheckService
from auto_check.ASL.ASLCheckService import ASLCheckService
from auto_check.AUO.AUOCheckService import AUOCheckService
from auto_check.AG4.AG4CheckService import AG4CheckService
from auto_check.ALM.ALMCheckService import ALMCheckService
from auto_check.ADD.ADDCheckService import ADDCheckService
from auto_check.AEW.AEWCheckService import AEWCheckService
from auto_check.AOD.AODCheckService import AODCheckService
from auto_check.AXY.AXYCheckService import AXYCheckService
from auto_check.AVB.AVBCheckService import AVBCheckService
from auto_check.AJA.AJACheckService import AJACheckService
from auto_check.ATK.ATKCheckService import ATKCheckService
from auto_check.AZ9.AZ9CheckService import AZ9CheckService
from utils.log import check_FZ_logger, check_6E_logger, check_UO_logger, check_G4_logger, check_DD_logger, \
    check_QG_logger, check_EW_logger, check_OD_logger, check_XY_logger, check_VB_logger, check_JA_logger, \
    check_TK_logger, check_B6_logger, check_SL_logger, check_Z9_logger

app = Flask(__name__)

"""
Check: 质检
NoShow: noShow
"""


@app.route("/Check/FZ", methods=["GET", "POST"])
def get_fz_check_info():
    result = None

    info_type = request.args.get("type")
    last_name = request.args.get("lastName")
    record_locator = request.args.get("recordLocator")

    check_FZ_logger.info(f"传入的参数为: "
                         f"type: {info_type}\n"
                         f"lastName: {last_name}\n"
                         f"recordLocator: {record_locator}\n")

    if info_type == 'all' or info_type == '':
        result = show_check_all_info(last_name, record_locator)

    elif info_type == "part":
        result = show_check_part_info(last_name, record_locator)

    else:
        check_FZ_logger.error("缺失Type参数或者参数不是all或part")

    return jsonify(result)


@app.route("/Check/6E", methods=["GET", "POST"])
def get_6e_check_info():
    result = None

    info_type = request.args.get("type")
    last_name = request.args.get("lastName")
    record_locator = request.args.get("recordLocator")

    check_FZ_logger.info(f"传入的参数为: "
                         f"type: {info_type}\n"
                         f"lastName: {last_name}\n"
                         f"recordLocator: {record_locator}\n")

    if info_type == 'all' or info_type == '':
        result = A6ECheckService.show_check_all_info(last_name, record_locator)

    elif info_type == "part":
        result = A6ECheckService.show_check_part_info(last_name, record_locator)

    else:
        check_6E_logger.error("缺失Type参数或者参数不是all或part")

    return jsonify(result)


@app.route("/Check/UO", methods=["GET", "POST"])
def get_uo_check_info():
    result = None

    info_type = request.args.get("type")
    last_name = request.args.get("lastName")
    first_name = request.args.get("firstName")
    record_locator = request.args.get("recordLocator")

    check_UO_logger.info(f"传入的参数为: \n"
                         f"type: {info_type}\n"
                         f"lastName: {last_name}\n"
                         f"firstName: {first_name}\n"
                         f"recordLocator: {record_locator}")

    if info_type == 'all' or info_type == '':
        result = AUOCheckService.show_check_all_info(last_name, first_name, record_locator)

    elif info_type == "part":
        result = AUOCheckService.show_check_part_info(last_name, first_name, record_locator)

    elif info_type == "agent":
        result = AUOCheckService.show_check_agent_info(pnr=record_locator)

    else:
        check_UO_logger.error("缺失Type参数或者参数不是all或part")

    return jsonify(result)


@app.route("/Check/G4", methods=["GET", "POST"])
def get_g4_check_info():
    result = None

    info_type = request.args.get("type")
    last_name = request.args.get("lastName")
    first_name = request.args.get("firstName")
    record_locator = request.args.get("recordLocator")

    check_G4_logger.info(f"传入的参数为: \n"
                         f"type: {info_type}\n"
                         f"lastName: {last_name}\n"
                         f"firstName: {first_name}\n"
                         f"recordLocator: {record_locator}")

    if info_type == 'all' or info_type == '':
        result = AG4CheckService.show_check_all_info(last_name, first_name, record_locator)

    elif info_type == "part":
        result = AG4CheckService.show_check_part_info(last_name, first_name, record_locator)

    else:
        check_G4_logger.error("缺失Type参数或者参数不是all或part")

    return jsonify(result)


@app.route("/Check/LM", methods=["GET", "POST"])
def get_lm_check_info():
    result = None

    info_type = request.args.get("type")
    last_name = request.args.get("lastName")
    record_locator = request.args.get("recordLocator")

    check_G4_logger.info(f"传入的参数为: \n"
                         f"type: {info_type}\n"
                         f"lastName: {last_name}\n"
                         f"recordLocator: {record_locator}")

    if info_type == 'all' or info_type == '':
        result = ALMCheckService.show_check_all_info(last_name, record_locator)

    elif info_type == "part":
        result = ALMCheckService.show_check_part_info(last_name, record_locator)

    else:
        check_G4_logger.error("缺失Type参数或者参数不是all或part")

    return jsonify(result)


@app.route("/Check/QG", methods=["GET", "POST"])
def get_qg_check_info():
    result = None

    info_type = request.args.get("type")
    last_name = request.args.get("lastName")
    record_locator = request.args.get("recordLocator")

    check_QG_logger.info(f"传入的参数为: \n"
                         f"type: {info_type}\n"
                         f"lastName: {last_name}\n"
                         f"recordLocator: {record_locator}")

    if info_type == 'all' or info_type == '':
        result = AQGCheckService.show_check_all_info(last_name, record_locator)

    elif info_type == "part":
        result = AQGCheckService.show_check_part_info(last_name, record_locator)

    else:
        check_QG_logger.error("缺失Type参数或者参数不是all或part")

    return jsonify(result)


@app.route("/Check/DD", methods=["GET", "POST"])
def get_dd_check_info():
    """
    DD 代理人质检
    :return:
    """

    result = None
    info_type = request.args.get("type")
    last_name = request.args.get("lastName")
    record_locator = request.args.get("recordLocator")
    check_DD_logger.info(f"传入的参数为: \n"
                         f"type: {info_type}\n"
                         f"lastName: {last_name}\n"
                         f"recordLocator: {record_locator}")

    if info_type == 'all' or info_type == '':
        result = ADDCheckService.show_check_all_info(last_name=last_name, pnr=record_locator)

    elif info_type == "part":
        pass
    elif info_type == "agent":
        result = ADDCheckService.show_check_agent_info(last_name=last_name, pnr=record_locator)
    else:
        check_DD_logger.error("缺失Type参数或者参数不是all或part")

    return jsonify(result)


@app.route("/Check/EW", methods=["GET", "POST"])
def get_ew_check_info():
    result = None

    info_type = request.args.get("type")
    last_name = request.args.get("lastName")
    record_locator = request.args.get("recordLocator")
    gender = request.args.get('gender')

    check_EW_logger.info(f"传入的参数为: \n"
                         f"type: {info_type}\n"
                         f"lastName: {last_name}\n"
                         f"recordLocator: {record_locator}\n"
                         f"gender: {gender}")

    if info_type == 'all' or info_type == '':
        result = AEWCheckService.show_check_all_info(last_name, record_locator, gender)

    elif info_type == "part":
        result = AEWCheckService.show_check_part_info(last_name, record_locator, gender)

    else:
        check_EW_logger.error("缺失Type参数或者参数不是all或part")

    return jsonify(result)


@app.route("/Check/OD", methods=["GET", "POST"])
def get_od_check_info():
    result = None

    info_type = request.args.get("type")
    record_locator = request.args.get("recordLocator")

    check_OD_logger.info(f"传入的参数为: \n"
                         f"type: {info_type}\n"
                         f"recordLocator: {record_locator}")

    if info_type == 'all' or info_type == '':
        result = AODCheckService.show_check_all_info(record_locator)

    elif info_type == "part":
        result = AODCheckService.show_check_part_info(record_locator)

    else:
        check_OD_logger.error("缺失Type参数或者参数不是all或part")

    return jsonify(result)


@app.route("/Check/XY", methods=["GET", "POST"])
def get_xy_check_info():
    result = None

    info_type = request.args.get("type")
    last_name = request.args.get("lastName")
    record_locator = request.args.get("recordLocator")

    check_OD_logger.info(f"传入的参数为: \n"
                         f"type: {info_type}\n"
                         f"lastName: {last_name}\n"
                         f"recordLocator: {record_locator}")

    if info_type == 'all' or info_type == '':
        result = AXYCheckService.show_check_all_info(last_name, record_locator)

    elif info_type == "part":
        result = AXYCheckService.show_check_part_info(last_name, record_locator)

    else:
        check_XY_logger.error("缺失Type参数或者参数不是all或part")

    return jsonify(result)


@app.route("/Check/VB", methods=["GET", "POST"])
def get_vb_check_info():
    result = None

    info_type = request.args.get("type")
    last_name = request.args.get("lastName")
    record_locator = request.args.get("recordLocator")

    check_VB_logger.info(f"传入的参数为: \n"
                         f"type: {info_type}\n"
                         f"lastName: {last_name}\n"
                         f"recordLocator: {record_locator}")

    if info_type == 'all' or info_type == '':
        result = AVBCheckService.show_check_all_info(last_name, record_locator)

    elif info_type == "part":
        result = AVBCheckService.show_check_part_info(last_name, record_locator)

    else:
        check_VB_logger.error("缺失Type参数或者参数不是all或part")

    return jsonify(result)


@app.route("/Check/JA", methods=["GET", "POST"])
def get_ja_check_info():
    result = None

    info_type = request.args.get("type")
    last_name = request.args.get("lastName")
    record_locator = request.args.get("recordLocator")

    check_JA_logger.info(f"传入的参数为: \n"
                         f"type: {info_type}\n"
                         f"lastName: {last_name}\n"
                         f"recordLocator: {record_locator}")

    if info_type == 'all' or info_type == '':
        result = AJACheckService.show_check_all_info(last_name, record_locator)

    elif info_type == "part":
        result = AJACheckService.show_check_part_info(last_name, record_locator)

    else:
        check_JA_logger.error("缺失Type参数或者参数不是all或part")

    return jsonify(result)


@app.route("/Check/TK", methods=["GET", "POST"])
def get_tk_check_info():
    result = None

    info_type = request.args.get("type")
    last_name = request.args.get("lastName")
    record_locator = request.args.get("recordLocator")

    check_TK_logger.info(f"传入的参数为: \n"
                         f"type: {info_type}\n"
                         f"lastName: {last_name}\n"
                         f"recordLocator: {record_locator}")

    if info_type == 'all' or info_type == '':
        result = ATKCheckService.show_check_all_info(last_name, record_locator)

    elif info_type == "part":
        result = ATKCheckService.show_check_part_info(last_name, record_locator)

    else:
        check_TK_logger.error("缺失Type参数或者参数不是all或part")

    return jsonify(result)


@app.route("/Check/B6", methods=["GET", "POST"])
def get_b6_check_info():
    result = None

    info_type = request.args.get("type")
    last_name = request.args.get("lastName")
    record_locator = request.args.get("recordLocator")

    check_TK_logger.info(f"传入的参数为: \n"
                         f"type: {info_type}\n"
                         f"lastName: {last_name}\n"
                         f"recordLocator: {record_locator}")

    if info_type == 'all' or info_type == '':
        result = AB6CheckService.show_check_all_info(last_name, record_locator)

    elif info_type == "part":
        result = AB6CheckService.show_check_part_info(last_name, record_locator)

    else:
        check_B6_logger.error("缺失Type参数或者参数不是all或part")

    return jsonify(result)


@app.route("/Check/SL", methods=['GET', 'POST'])
def get_sl_check_info():
    result = None

    info_type = request.args.get("type")
    last_name = request.args.get("lastName")
    first_name = request.args.get("firstName")
    record_locator = request.args.get("recordLocator")
    otaid = request.args.get("otaId")
    check_SL_logger.info(f"otaid: {otaid}")
    check_SL_logger.info(f"传入的参数为: \n"
                         f"type: {info_type}\n"
                         f"lastName: {last_name}\n"
                         f"firstName: {first_name}\n"
                         f"recordLocator: {record_locator}\n"
                         f"otaId: {otaid}")

    if info_type == 'all' or info_type == '':
        result = ASLCheckService.show_check_all_info(last_name=last_name, first_name=first_name,pnr=record_locator, otaid=otaid)

    elif info_type == "part":
        check_SL_logger.error("part 暂不支持")
        pass
    else:
        check_SL_logger.error("缺失Type参数或者参数不是all或part")

    return jsonify(result)


@app.route("/Check/Z9", methods=['GET', 'POST'])
def get_z9_check_info():
    result = None

    info_type = request.args.get("type")
    last_name = request.args.get("lastName")
    record_locator = request.args.get("recordLocator")

    check_Z9_logger.info(f"传入的参数为: \n"
                         f"type: {info_type}\n"
                         f"lastName: {last_name}\n"
                         f"recordLocator: {record_locator}")

    if info_type == 'all' or info_type == '':
        result = AZ9CheckService.show_check_all_info(last_name=last_name, pnr=record_locator)

    elif info_type == "part":
        result = AZ9CheckService.show_check_part_info(last_name=last_name, pnr=record_locator)
    else:
        check_Z9_logger.error("缺失Type参数或者参数不是all或part")

    return jsonify(result)


# -------------------------------定时检查PNR任务接口------------------------------

from auto_check.AU2.AU2CheckService import AU2PnrService
from auto_check.ASL.ASLCheckApi import ASLCheckWeb


@app.route("/Check/PNR/U2", methods=['GET', 'POST'])
def get_u2_pnr_info():
    AU2PnrService.check_pnr_status()


@app.route("/Check/tests", methods=['GET', 'POST'])
def get_tests():
    app = ASLCheckWeb()
    app.front_check(last_name="WANG", first_name="YOU SIANG", pnr="WPRUBB")
    app.redirect_1()
    app.redirect_2()
    app.check()
    # app.get_baggage_redirect1()
    # app.get_baggage_html()


def task():
    from flask_apscheduler import APScheduler
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.add_job(id='U2', func=get_u2_pnr_info, trigger='interval', hours=5, jitter=120, start_date='2022-12-29 15:05:00')
    # scheduler.add_job(id='SL_test', func=get_tests, trigger='interval', seconds=30, jitter=120)
    scheduler.start()

