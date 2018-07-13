import pickle
from selenium import webdriver
import time
from weibo.Connect_mysql import Connect


def get():
    conf, engine = Connect('conf.yaml')  # 获取配置文件的内容
    loginname = conf.get('loginname')
    password = conf.get('password')

    loginname = list(loginname.values())
    password = list(password.values())
    with open('cookies.pkl', 'wb') as f:
        for i in range(len(password)):  # 将每个账号的cookies保存下来.
            try:
                driver = webdriver.Chrome()
                driver.set_window_size(1124, 850)  # 防止得到的WebElement的状态is_displayed为False，即不可见
                driver.get("http://www.weibo.com/login.php")
                time.sleep(5)
                driver.find_element_by_xpath('//*[@id="loginname"]').clear()
                driver.find_element_by_xpath('//*[@id="loginname"]').send_keys(loginname[i])
                driver.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[2]/div/input').clear()

                time.sleep(2)
                driver.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[2]/div/input').send_keys(
                    password[i])
                driver.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a').click()

                driver.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[3]/div/input').send_keys(
                    input("输入验证码： "))

                time.sleep(1)
                driver.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a').click()
            except Exception as e:
                print(e)
                time.sleep(1)

            cookies = driver.get_cookies()
            print(cookies)
            pickle.dump(cookies, f)


if __name__ == '__main__':
    get()
