from disc import discriminant

# D >= 0
def test_positive():
    assert discriminant(1, -5, 6) == 1
    assert discriminant(1, 0, 0) == 0   
    assert discriminant(2, 4, 2) == 0   

# D < 0
def test_negative():
    assert discriminant(1, 2, 3) == -8  
    assert discriminant(3, 1, 1) == -11 
