def recommend_fertilizer(age_year, age_month, N_avail, P_avail, K_avail):
    
    # Step 1: Define annual NPK table
    npk_table = {
        1: {'N': 110, 'P': 0,   'K': 110},
        2: {'N': 220, 'P': 0,   'K': 220},
        3: {'N': 330, 'P': 0,   'K': 330},
        4: {'N': 440, 'P': 220, 'K': 440},
        5: {'N': 550, 'P': 275, 'K': 550},
        6: {'N': 660, 'P': 330, 'K': 660},
        7: {'N': 770, 'P': 385, 'K': 770},
        8: {'N': 880, 'P': 440, 'K': 880}
    }



    # Step 2: Handle age limit
    if age_year < 1:
        age_year = 1
    elif age_year > 8:
        age_year = 8


    # Step 3: Get annual requirement
    annual_N = npk_table[age_year]['N']
    annual_P = npk_table[age_year]['P']
    annual_K = npk_table[age_year]['K']


    # Step 4: Convert to monthly 
    monthly_N = annual_N / 12
    monthly_P = annual_P / 12
    monthly_K = annual_K / 12


    # Step 5: Calculate deficit 
    deficit_N = max(monthly_N - N_avail, 0)
    deficit_P = max(monthly_P - P_avail, 0)
    deficit_K = max(monthly_K - K_avail, 0)


    # Step 6: Convert to fertilizers 
    urea = deficit_N / 0.46      # 46% N
    ssp  = deficit_P / 0.16      # 16% P
    mop  = deficit_K / 0.60      # 60% K


    # Step 7: Return results 
    return {
        "monthly_required_N": round(monthly_N, 2),
        "monthly_required_P": round(monthly_P, 2),
        "monthly_required_K": round(monthly_K, 2),
        
        "deficit_N": round(deficit_N, 2),
        "deficit_P": round(deficit_P, 2),
        "deficit_K": round(deficit_K, 2),
        
        "urea": round(urea, 2),
        "ssp": round(ssp, 2),
        "mop": round(mop, 2)
    }