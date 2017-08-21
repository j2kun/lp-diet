def load(filename):
    with open(filename, 'rb') as infile:
        contents = infile.read().decode('iso-8859-1')
    lines = contents.replace('\r', '').split('\n')
    return [[x.strip('~') for x in line.split('^')] for line in lines]


abbrev_column_names = '''id
description
water (g)
energy (kcal)
protein (g)
total fat (g)
ash (g)
carbohydrate (g)
dietary fiber (g)
sugar (g)
calcium (mg)
iron (mg)
magnesium (mg)
phosphorus (mg)
potassium (mg)
sodium (mg)
zinc (mg)
copper (mg)
manganese (mg)
selenium (μg)
vitamin c (mg)
thiamin (mg)
riboflavin (mg)
niacin (mg)
pantothenic acid (mg)
vitamin b6 (mg)
total folate (μg)
folic acid (μg)
food folate (μg)
dietary folate equivalents (μg)
choline (mg)
vitamin b12 (μg)
vitamin a (iu)
vitamin a retinol activity equivalents (μg)
retinol (μg)
alpha-carotene (μg)
beta-carotene (μg)
beta-cryptoxanthin (μg)
lycopene (μg)
lutein + zeazanthin (μg)
vitamin e (alpha-tocopherol) (mg)
vitamin d (μg)
vitamin d (iu)
vitamin k (phylloquinone) (μg)
saturated fatty acid (g)
monounsaturated fatty acids (g)
polyunsaturated fatty acids (g)
cholesterol (mg)
first household weight
first household weight description
second household weight
second household weight description
percent refuse'''.split('\n')



'''
Example data point in FOOD_DES.txt:

    ndb_id: '01001',
    food_group_code: '0100',
    long_description: 'Butter, salted',   # 200-char max
    short_description: 'BUTTER,WITH SALT',  # 60-char max
    common_name: '',
    manufacturer_name: '',
    in_fndds: 'Y',
    refuse_description: '',
    percentage_refuse: '0',
    scientific_name: '',  # only for unprocessed foods
    nitrogen_to_protein_factor: '6.38',
    calories_from_protein_factor: '4.27',
    calories_from_fat_factor: '8.79',
    caories_from_carbs_factor: '3.87'


Example data point in NUTR_DEF.txt:

    id: '203'
    units: 'g'
    tagname: 'PROCNT'   # used by INFOODS database
    description: 'Protein'
    precision: '2'   # number of decimal places to which nutrient is rounded
    sr_order: '600'  # sorting key (useless)


Example data point in NUT_DATA.txt:

    food_id: '01140',
    nutriend_id: '269',
    amount_100g: '0.40',
    num_data_points: '0',
    std_error: '',
    data_type_code: '4',
    data_derivation_code: 'BFCN',
    reference_ndb_no: '01123',
    added_nutrient_mark: '',   # added nutrients for some breakfast cereals
    num_studies: '',
    min_value: '',
    max_value: '',
    degrees_of_freedom: '',
    lower_bound_95: '',
    upper_bound_95: '',
    statistical_comments: '',
    date_updated: '02/2009',
    confidence_code: ''
'''
