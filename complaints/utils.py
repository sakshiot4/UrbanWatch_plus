# complaints/utils.py

def get_region_from_pincode(pincode):
    """
    Maps a Mumbai pincode to a specific region (North, South, East, West).
    """
    # South Mumbai (Colaba, Fort, Malabar Hill, etc.)
    SOUTH_MUMBAI = ['400001', '400002', '400003', '400004', '400005', '400006', '400020', '400032']
    
    # West Mumbai (Bandra, Andheri, Juhu, Khar, Santacruz)
    WEST_MUMBAI = ['400050', '400051', '400052', '400053', '400054', '400058',  ]
    
    # East Mumbai (Kurla, Chembur, Ghatkopar, Mulund)
    EAST_MUMBAI = ['400070', '400071', '400074', '400075', '400077', '400080']
    
    # North Mumbai (Borivali, Kandivali, Malad, Goregaon)
    NORTH_MUMBAI = ['400067', '400091', '400092', '400064', '400097']

    if pincode in SOUTH_MUMBAI:
        return 'south'
    elif pincode in WEST_MUMBAI:
        return 'west'
    elif pincode in EAST_MUMBAI:
        return 'east'
    elif pincode in NORTH_MUMBAI:
        return 'north'
    else:
        return 'central' # Default if pincode is not in our list