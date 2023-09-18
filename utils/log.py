import logging
from utils.logger import LOGGING, register_log
from logging.config import dictConfig

register_log("Grasp")  # 抓取日志
register_log("Robot")  # Robot日志集合
register_log("Pay")
register_log("Spider")  # 5J日志
register_log("Api")  # 5J支付日志
register_log("AutoApplyCard")
register_log("DingTalk")
register_log("Verification")
register_log("Spider_6J")
register_log('Booking_6J')
register_log('Booking_DD')
register_log("Spider_AE")
register_log("Spider_B7")


register_log('Spider_bag')
register_log('Spider_V7')
register_log('Spider_H2')
register_log('Spider_G8')
register_log('Spider_SG')
register_log('Spider_2I')
register_log('Spider_GQ')
register_log('Spider_TO')
register_log('Spider_TS')
register_log('Spider_WS')
register_log('Spider_LS')
register_log('Spider_6E')
register_log('Spider_T3')
register_log('Spider_XP')
register_log('Spider_G4')
register_log('Spider_BC')
register_log('Spider_FD')
register_log('Spider_N0')
register_log('Spider_BZ')
register_log('Spider_Y9')
register_log('Spider_TL')
register_log('Spider_FY')
register_log('Spider_J9')
register_log('Spider_BF')
register_log('Spider_DD')
register_log('Spider_YQ')
register_log('Spider_OV')
register_log('Spider_FO')
register_log('Spider_Z9')

register_log('Check_FZ')
register_log('Check_6E')
register_log('Check_UO')
register_log('Check_G4')
register_log('Check_LM')
register_log('Check_QG')
register_log('Check_DD')
register_log('Check_EW')
register_log('Check_OD')
register_log('Check_XY')
register_log('Check_VB')
register_log('Check_JA')
register_log('Check_SL')
register_log('Check_TO')
register_log('Check_TK')
register_log('Check_B6')
register_log('Check_Z9')

# 定时检查PNR状态
register_log('Check_PNR_U2')

register_log('Refund_6J')
register_log('Refund_Check_6J')
register_log('add_on')
register_log('Refund_VY')
register_log('Refund_6E')
register_log('Refund_Check_VY')
register_log('Booking_VY')
register_log('Booking_6E')
register_log('Refund_Check_6E')
register_log('ADD_ON_5J')
register_log('ADD_ON_VB')
register_log('Booking_VB')
register_log("Booking_5j")  # 预定日志
register_log("Spider_5j")  # 5J日志
register_log("Booking_XY")
register_log("ADD_ON_XY")
register_log("Booking_Z9")
register_log("Booking_G8")
register_log("Booking_FZ")
register_log("ADD_ON_G8")
register_log("ADD_ON_FZ")
register_log('ADD_ON_Z9')
register_log('Refund_VY_Full')


dictConfig(LOGGING)
check_5J_logger = logging.getLogger("Check_5J")
logger = logging.getLogger("Grasp")
spider_logger = logging.getLogger('Spider')
spider_VY_logger = logging.getLogger('Spider_VY')
refund_VY_logger = logging.getLogger('Refund_VY')
refund_6E_logger = logging.getLogger('Refund_6E')
booking_VY_logger = logging.getLogger('Booking_VY')
refund_check_VY_logger = logging.getLogger('Refund_Check_VY')
refund_check_6E_logger = logging.getLogger('Refund_Check_6E')
spider_6J_logger = logging.getLogger('Spider_6J')
booking_6J_logger = logging.getLogger('Booking_6J')
refund_6J_logger = logging.getLogger('Refund_6J')
refund_check_6J_logger = logging.getLogger('Refund_Check_6J')
spider_5j_logger = logging.getLogger('Spider_5j')
robot_5j_logger = logging.getLogger('Booking_5j')
robot_VB_logger = logging.getLogger('Booking_VB')
robot_XY_logger = logging.getLogger('Booking_XY')
robot_G8_logger = logging.getLogger("Booking_G8")
robot_FZ_logger = logging.getLogger("Booking_FZ")
spider_AE_logger = logging.getLogger('Spider_AE')
refund_VY_Full_logger = logging.getLogger('Refund_VY_Full')


booking_6E_logger = logging.getLogger('Booking_6E')
booking_DD_logger = logging.getLogger('Booking_DD')
booking_Z9_logger = logging.getLogger('Booking_Z9')


pay_logger = logging.getLogger('Pay')
robot_logger = logging.getLogger('Robot')
api_logger = logging.getLogger('Api')
card_logger = logging.getLogger("AutoApplyCard")
ding_talk_log = logging.getLogger("DingTalk")
verification_log = logging.getLogger("Verification")
spider_bag_log = logging.getLogger('Spider_bag')

spider_V7_logger = logging.getLogger('Spider_V7')

spider_H2_logger = logging.getLogger('Spider_H2')

spider_G8_logger = logging.getLogger('Spider_G8')

spider_SG_logger = logging.getLogger('Spider_SG')

spider_2I_logger = logging.getLogger('Spider_2I')

spider_GQ_logger = logging.getLogger('Spider_GQ')

spider_TO_logger = logging.getLogger('Spider_TO')

spider_TS_logger = logging.getLogger('Spider_TS')

spider_WS_logger = logging.getLogger('Spider_WS')

spider_LS_logger = logging.getLogger('Spider_LS')

spider_6E_logger = logging.getLogger('Spider_6E')

spider_6e_logger = logging.getLogger('Spider_6e')

spider_T3_logger = logging.getLogger('Spider_T3')

spider_XP_logger = logging.getLogger('Spider_XP')

spider_G4_logger = logging.getLogger("Spider_G4")

spider_BC_logger = logging.getLogger('Spider_BC')

spider_FD_logger = logging.getLogger('Spider_FD')

spider_N0_logger = logging.getLogger('Spider_N0')

spider_BZ_logger = logging.getLogger('Spider_BZ')

spider_Y9_logger = logging.getLogger('Spider_Y9')

spider_TL_logger = logging.getLogger('Spider_TL')

spider_FY_logger = logging.getLogger('Spider_FY')

spider_J9_logger = logging.getLogger('Spider_J9')

spider_HD_logger = logging.getLogger('Spider_HD')

spider_BF_logger = logging.getLogger('Spider_BF')

spider_DD_logger = logging.getLogger('Spider_DD')

spider_YQ_logger = logging.getLogger('Spider_YQ')

spider_OV_logger = logging.getLogger('Spider_OV')

spider_FO_logger = logging.getLogger('Spider_FO')

spider_Z9_logger = logging.getLogger('Spider_Z9')

spider_B7_logger = logging.getLogger('Spider_B7')

# 质检日志
check_FZ_logger = logging.getLogger('Check_FZ')
check_6E_logger = logging.getLogger('Check_6E')
check_UO_logger = logging.getLogger('Check_UO')
check_G4_logger = logging.getLogger('Check_G4')
check_LM_logger = logging.getLogger('Check_LM')
check_QG_logger = logging.getLogger('Check_QG')
check_DD_logger = logging.getLogger('Check_DD')
add_on_logger = logging.getLogger('add_on')
check_EW_logger = logging.getLogger('Check_EW')
check_OD_logger = logging.getLogger('Check_OD')
check_XY_logger = logging.getLogger('Check_XY')
check_VB_logger = logging.getLogger('Check_VB')
check_JA_logger = logging.getLogger('Check_JA')
check_SL_logger = logging.getLogger('Check_SL')
check_TO_logger = logging.getLogger('Check_TO')
check_TK_logger = logging.getLogger('Check_TK')
check_B6_logger = logging.getLogger('Check_B6')
check_Z9_logger = logging.getLogger('Check_Z9')

# 定时检查PNR状态日志
check_PNR_U2_logger = logging.getLogger('Check_PNR_U2')

add_on_5j_logger = logging.getLogger('ADD_ON_5J')
add_on_VB_logger = logging.getLogger('ADD_ON_VB')
add_on_XY_logger = logging.getLogger('ADD_ON_XY')
add_on_G8_logger = logging.getLogger('ADD_ON_G8')

add_on_FZ_logger = logging.getLogger('ADD_ON_FZ')
add_on_Z9_logger = logging.getLogger('ADD_ON_Z9')
