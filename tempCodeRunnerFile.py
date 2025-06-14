    hero_elements = driver.find_elements(By.CSS_SELECTOR, 'css_selector_do_elementow_bohaterow')

    for elem in hero_elements:
        # Kliknij element lewym przyciskiem myszy
        ActionChains(driver).move_to_element(elem).click().perform()

        # Poczekaj chwilę na pojawienie się tooltipa lub info
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'css_selector_tooltipu_z_nazwa_bohatera'))
        )

        # Pobierz tekst z tooltipu
        tooltip = driver.find_element(By.CSS_SELECTOR, 'css_selector_tooltipu_z_nazwa_bohatera')
        print("Hero name:", tooltip.text)