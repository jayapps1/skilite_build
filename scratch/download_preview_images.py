import os
import time
import urllib.request
import io
from PIL import Image, ImageDraw, ImageFont

# Define static directories
BASE_DIR = r"d:\skilite-build"
PREVIEWS_DIR = os.path.join(BASE_DIR, "static", "images", "previews")

# Map category slugs to folder names
CATEGORY_FOLDER_MAP = {
    "technology": "technology",
    "finance": "finance",
    "restaurant-food": "restaurant",
    "healthcare": "healthcare",
    "education": "education",
    "beauty-cosmetics": "beauty",
    "construction": "construction",
    "logistics-transport": "logistics",
    "fashion": "fashion",
    "real-estate": "real-estate",
    "hospitality-tourism": "tourism",
    "agriculture": "agriculture",
    "corporate-services": "corporate",
    "nonprofit-ngo": "nonprofit",
    "default": "fallback"
}

# Image sizes & targets
# Hero desktop: 1600x900
# Hero mobile: 900x1200
# Content banner (about, contact, cta): 1200x700
# Card / Product / Gallery: 800x600
# Portrait (team, testimonial): 500x500
# Cover: 1200x450
# Logo: 200x200
IMAGE_DIMENSIONS = {
    "hero_desktop": (1600, 900),
    "hero_mobile": (900, 1200),
    "about": (1200, 700),
    "product_1": (800, 600),
    "product_2": (800, 600),
    "product_3": (800, 600),
    "product_4": (800, 600),
    "product_5": (800, 600),
    "product_6": (800, 600),
    "gallery_1": (800, 600),
    "gallery_2": (800, 600),
    "gallery_3": (800, 600),
    "team_1": (500, 500),
    "team_2": (500, 500),
    "team_3": (500, 500),
    "testimonial_1": (400, 400),
    "testimonial_2": (400, 400),
    "testimonial_3": (400, 400),
    "contact": (1200, 700),
    "cta": (1200, 700),
    "cover": (1200, 450),
    "logo": (200, 200)
}

# Target file size guidelines (quality selection dynamically reduces output weight)
TARGET_QUALITY = {
    "hero_desktop": 80,
    "hero_mobile": 75,
    "about": 80,
    "product_1": 80,
    "product_2": 80,
    "product_3": 80,
    "product_4": 80,
    "product_5": 80,
    "product_6": 80,
    "gallery_1": 80,
    "gallery_2": 80,
    "gallery_3": 80,
    "team_1": 75,
    "team_2": 75,
    "team_3": 75,
    "testimonial_1": 75,
    "testimonial_2": 75,
    "testimonial_3": 75,
    "contact": 80,
    "cta": 80,
    "cover": 80,
    "logo": 85
}

# Curated high-quality Unsplash IDs per category (18-24 distinct photos)
UNSPLASH_IDS = {
    "restaurant-food": {
        "hero_desktop": "photo-1544025162-d76694265947", # plated chicken & Jollof style
        "hero_mobile": "photo-1565299624946-b28f40a0ae38", # food close up vertical
        "about": "photo-1556910103-1c02745aae4d", # stovetop cooking
        "product_1": "photo-1512058564366-18510be2db19", # Jollof/rice bowl
        "product_2": "photo-1519708227418-c8fd9a32b7a2", # grilled fish
        "product_3": "photo-1547592180-85f173990554", # soup bowl
        "product_4": "photo-1546069901-ba9599a7e63c", # salad/grain platter
        "product_5": "photo-1567620905732-2d1ec7ab7445", # sweet plantain slices
        "product_6": "photo-1497534446932-c925b458314e", # hibiscus Sobolo drink
        "gallery_1": "photo-1550966871-3ed3cdb5ed0c", # modern restaurant tables
        "gallery_2": "photo-1559339352-11d035aa65de", # restaurant dining bar
        "gallery_3": "photo-1514933651103-005eec06c04b", # outside garden seating
        "team_1": "photo-1577219491135-ce391730fb2c", # Executive Head Chef
        "team_2": "photo-1583394838336-acd977736f90", # Pastry Chef
        "team_3": "photo-1595273670150-db0d3bf3b7cc", # Sous Chef
        "testimonial_1": "photo-1534528741775-53994a69daeb", # Sarah Jenkins
        "testimonial_2": "photo-1507003211169-0a1dd7228f2d", # David Osei
        "testimonial_3": "photo-1494790108377-be9c29b29330", # Rebecca Mensah
        "contact": "photo-1522336572018-94d9572113df", # restaurant exterior/entrance
        "cta": "photo-1414235077428-338989a2e8c0", # elegant dinner service tray
        "cover": "photo-1554118811-1e0d58224f24", # cozy café banner cover
        "logo": "photo-1556911220-e15b29be8c8f" # plated fork logo
    },
    "technology": {
        "hero_desktop": "photo-1531403009284-440f080d1e12", # technology team workspace dashboard
        "hero_mobile": "photo-1551434678-e076c223a692", # coder working vertical
        "about": "photo-1522071820081-009f0129c71c", # team collaborating on code
        "product_1": "photo-1551288049-bebda4e38f71", # analytics dashboard
        "product_2": "photo-1451187580459-43490279c0fa", # cloud abstract server database
        "product_3": "photo-1563986768609-322da13575f3", # cybersecurity digital lock
        "product_4": "photo-1460925895917-afdab827c52f", # cloud computing web platform
        "product_5": "photo-1504868584819-f8e8b4b6d7e3", # automated dashboard CRM
        "product_6": "photo-1618005182384-a83a8bd57fbe", # AI deep learning nodes
        "gallery_1": "photo-1519389950473-47ba0277781c", # computing office monitor rows
        "gallery_2": "photo-1526374965328-7f61d4dc18c5", # blue neon server rack
        "gallery_3": "photo-1517245386807-bb43f82c33c4", # lounge computing collaboration
        "team_1": "photo-1560250097-0b93528c311a", # CTO
        "team_2": "photo-1573496359142-b8d87734a5a2", # Cloud Engineer
        "team_3": "photo-1519085360753-af0119f7cbe7", # AI Specialist
        "testimonial_1": "photo-1500648767791-00dcc994a43e", # Client A
        "testimonial_2": "photo-1544005313-94ddf0286df2", # Client B
        "testimonial_3": "photo-1506794778202-cad84cf45f1d", # Client C
        "contact": "photo-1486406146926-c627a92ad1ab", # glass HQ tower
        "cta": "photo-1522202176988-66273c2fd55f", # joint strategy consultation
        "cover": "photo-1618005182384-a83a8bd57fbe", # binary wave pattern cover
        "logo": "photo-1516321318423-f06f85e504b3" # tech emblem
    },
    "finance": {
        "hero_desktop": "photo-1454165804606-c3d57bc86b40", # professional business consultations
        "hero_mobile": "photo-1559526324-4b87b5e36e44", # advisor talking vertical
        "about": "photo-1551836022-d5d88e9218df", # workspace board strategy
        "product_1": "photo-1579621970563-ebec7560ff3e", # wealth savings vault coins
        "product_2": "photo-1590283603385-17ffb3a7f29f", # trading stock index
        "product_3": "photo-1611974789855-9c2a0a7236a3", # investment analytics spreadsheet
        "product_4": "photo-1563986768609-322da13575f3", # corporate secure banking
        "product_5": "photo-1554224155-8d04cb21cd6c", # tax invoicing accounting
        "product_6": "photo-1460925895917-afdab827c52f", # SME credit lines
        "gallery_1": "photo-1486406146926-c627a92ad1ab", # finance center offices
        "gallery_2": "photo-1491336477066-31156b5e4f35", # corporate handshakes
        "gallery_3": "photo-1522071820081-009f0129c71c", # portfolio review team
        "team_1": "photo-1560250097-0b93528c311a", # Principal Partner
        "team_2": "photo-1573496359142-b8d87734a5a2", # Portfolio Strategist
        "team_3": "photo-1519085360753-af0119f7cbe7", # Corporate Broker
        "testimonial_1": "photo-1534528741775-53994a69daeb",
        "testimonial_2": "photo-1507003211169-0a1dd7228f2d",
        "testimonial_3": "photo-1494790108377-be9c29b29330",
        "contact": "photo-1582533561751-ef6f6ab93a2e", # headquarters entrance lobby
        "cta": "photo-1454165804606-c3d57bc86b40", # consultation desks
        "cover": "photo-1507679799987-c73779587ccf", # boardroom desks cover
        "logo": "photo-1516321318423-f06f85e504b3" # corporate stamp logo
    },
    "healthcare": {
        "hero_desktop": "photo-1532938911079-1b06ac7ceec7", # doctor consulting with clinic patient
        "hero_mobile": "photo-1584515901407-c81216892404", # specialist doctor vertical
        "about": "photo-1629909613654-28e377c37b09", # modern clean medical ward
        "product_1": "photo-1603398938378-e54eab446dde", # cardiology screening monitor
        "product_2": "photo-1576091160550-2173dba999ef", # pediatric doctor screening
        "product_3": "photo-1581594693702-fbdc51b2763b", # laboratory diagnostics test
        "product_4": "photo-1584308666744-24d5c474f2ae", # pharmaceutical prescriptions
        "product_5": "photo-1516549655169-df83a0774514", # family nurse practitioner
        "product_6": "photo-1505751172876-fa1923c5c528", # dental wellness checks
        "gallery_1": "photo-1629909613654-28e377c37b09", # bright reception lobby
        "gallery_2": "photo-1519494026892-80bbd2d6fd0d", # hospital corridor
        "gallery_3": "photo-1579684389782-64d84b5e901d", # ultrasound scanners
        "team_1": "photo-1559839734-2b71ea197ec2", # Chief Medical Officer
        "team_2": "photo-1622253692010-333f2da6031d", # Pediatrician Specialist
        "team_3": "photo-1594824813573-246434e33963", # Resident Surgeon
        "testimonial_1": "photo-1544005313-94ddf0286df2",
        "testimonial_2": "photo-1506794778202-cad84cf45f1d",
        "testimonial_3": "photo-1500648767791-00dcc994a43e",
        "contact": "photo-1519494026892-80bbd2d6fd0d", # health center entry
        "cta": "photo-1622253692010-333f2da6031d", # doctor portrait pose
        "cover": "photo-1629909613654-28e377c37b09", # clean clinic banner cover
        "logo": "photo-1606811971618-4486d14f3f99" # clinical cross logo
    },
    "education": {
        "hero_desktop": "photo-1522202176988-66273c2fd55f", # college students learning together
        "hero_mobile": "photo-1523240795612-9a054b0db644", # student reading vertical
        "about": "photo-1427504494785-3a9ca7044f45", # highschool campus library
        "product_1": "photo-1581091226825-a6a2a5aee158", # computer programming class
        "product_2": "photo-1551288049-bebda4e38f71", # data analytics course
        "product_3": "photo-1561089489-f13d5e730d72", # design engineering course
        "product_4": "photo-1451187580459-43490279c0fa", # cloud network bootcamp
        "product_5": "photo-1544717305-2782549b5136", # study textbooks guidelines
        "product_6": "photo-1516321318423-f06f85e504b3", # interactive lectures
        "gallery_1": "photo-1523240795612-9a054b0db644", # students grouping
        "gallery_2": "photo-1516321318423-f06f85e504b3", # computers labs tables
        "gallery_3": "photo-1524178232363-1fb2b075b655", # lecture seminar hall
        "team_1": "photo-1573496359142-b8d87734a5a2", # Head of Admissions
        "team_2": "photo-1560250097-0b93528c311a", # Engineering Instructor
        "team_3": "photo-1544005313-94ddf0286df2", # Design Mentor
        "testimonial_1": "photo-1534528741775-53994a69daeb",
        "testimonial_2": "photo-1507003211169-0a1dd7228f2d",
        "testimonial_3": "photo-1494790108377-be9c29b29330",
        "contact": "photo-1523240795612-9a054b0db644", # school gates entry
        "cta": "photo-1522202176988-66273c2fd55f", # college workspace desks
        "cover": "photo-1427504494785-3a9ca7044f45", # library desks cover
        "logo": "photo-1546410531-bb4caa6b424d" # graduation mortarboard logo
    },
    "beauty-cosmetics": {
        "hero_desktop": "photo-1560750588-73207b1ef5b8", # premium salon spa facial
        "hero_mobile": "photo-1487412720507-e7ab37603c6f", # cosmetics portrait vertical
        "about": "photo-1522337360788-8b13dee7a37e", # modern elegance salon interiors
        "product_1": "photo-1600334089648-b0d9d3028eb2", # organic hydrating spa mask
        "product_2": "photo-1600334188905-c93d5bd5a4b1", # relaxing volcanic stones massage
        "product_3": "photo-1522337360788-8b13dee7a37e", # classic manicures gel cure
        "product_4": "photo-1487412720507-e7ab37603c6f", # bridal styling cosmetics
        "product_5": "photo-1512496015851-a90fb38ba796", # shea-butter skincare bottles
        "product_6": "photo-1515688594390-b649af70d282", # lavender essential oils
        "gallery_1": "photo-1519699047748-de8e457a634e", # wellness tables spa
        "gallery_2": "photo-1600334089648-b0d9d3028eb2", # skincare floral treatments
        "gallery_3": "photo-1522337360788-8b13dee7a37e", # vanity mirrors sets
        "team_1": "photo-1534528741775-53994a69daeb", # Lead Esthetician
        "team_2": "photo-1544005313-94ddf0286df2", # Hair Stylist Specialist
        "team_3": "photo-1494790108377-be9c29b29330", # Makeup Artist
        "testimonial_1": "photo-1506794778202-cad84cf45f1d",
        "testimonial_2": "photo-1507003211169-0a1dd7228f2d",
        "testimonial_3": "photo-1500648767791-00dcc994a43e",
        "contact": "photo-1522337360788-8b13dee7a37e", # luxury salon entrance
        "cta": "photo-1560750588-73207b1ef5b8", # relaxing therapy session
        "cover": "photo-1512496015851-a90fb38ba796", # flowers cosmetics banner
        "logo": "photo-1522337360788-8b13dee7a37e" # cosmetic bloom logo
    },
    "construction": {
        "hero_desktop": "photo-1541888946425-d81bb19240f5", # completed heavy architecture block
        "hero_mobile": "photo-1504307651254-35680f356dfd", # site builder with helmet vertical
        "about": "photo-1504917595217-d4dc5ebe6122", # structural engineer maps inspection
        "product_1": "photo-1590069261209-f8e9b8642343", # commercial concrete foundation pour
        "product_2": "photo-1504307651254-35680f356dfd", # blueprints architecture planning
        "product_3": "photo-1486406146926-c627a92ad1ab", # steel skyscraper framework build
        "product_4": "photo-1581094288338-2314dddb7ecc", # civil heavy earthworks grading
        "product_5": "photo-1504917595217-d4dc5ebe6122", # building zoning permits
        "product_6": "photo-1590674899484-d5640e854abe", # industrial piling foundations
        "gallery_1": "photo-1541888946425-d81bb19240f5", # high-rise modern skyline
        "gallery_2": "photo-1504307651254-35680f356dfd", # active builders crane site
        "gallery_3": "photo-1581094288338-2314dddb7ecc", # excavation fleet loader
        "team_1": "photo-1560250097-0b93528c311a", # Project Manager
        "team_2": "photo-1519085360753-af0119f7cbe7", # Chief Surveyor
        "team_3": "photo-1573496359142-b8d87734a5a2", # Safety Manager
        "testimonial_1": "photo-1534528741775-53994a69daeb",
        "testimonial_2": "photo-1507003211169-0a1dd7228f2d",
        "testimonial_3": "photo-1494790108377-be9c29b29330",
        "contact": "photo-1582533561751-ef6f6ab93a2e", # headquarters entrance
        "cta": "photo-1504917595217-d4dc5ebe6122", # planning meeting review
        "cover": "photo-1541888946425-d81bb19240f5", # raw concrete structure cover
        "logo": "photo-1581092160607-ee22621dd758" # steel girder logo
    },
    "logistics-transport": {
        "hero_desktop": "photo-1586528116311-ad8dd3c8310d", # modern container shipping yards
        "hero_mobile": "photo-1601584115197-04ecc0da31d7", # delivery transport van vertical
        "about": "photo-1586528116311-ad8dd3c8310d", # automated warehouse sorting center
        "product_1": "photo-1586528116311-ad8dd3c8310d", # regional heavy cargo freight
        "product_2": "photo-1566577134770-3d85bb3a9cc4", # express parcel dispatch messenger
        "product_3": "photo-1601584115197-04ecc0da31d7", # cold storage cargo supply
        "product_4": "photo-1521791136366-3e283b6f007c", # customs document clearance
        "product_5": "photo-1578575437130-527eed3abbec", # transit cardboard boxes
        "product_6": "photo-1590486803833-2c7087560b3c", # fleet line logistics
        "gallery_1": "photo-1586528116311-ad8dd3c8310d", # sorting hub corridor
        "gallery_2": "photo-1601584115197-04ecc0da31d7", # truck shipping bays
        "gallery_3": "photo-1578575437130-527eed3abbec", # parcel packing line
        "team_1": "photo-1560250097-0b93528c311a", # Logistics Director
        "team_2": "photo-1519085360753-af0119f7cbe7", # Fleet Captain
        "team_3": "photo-1573496359142-b8d87734a5a2", # Broker Partner
        "testimonial_1": "photo-1534528741775-53994a69daeb",
        "testimonial_2": "photo-1507003211169-0a1dd7228f2d",
        "testimonial_3": "photo-1494790108377-be9c29b29330",
        "contact": "photo-1582533561751-ef6f6ab93a2e", # terminal offices front
        "cta": "photo-1586528116311-ad8dd3c8310d", # freight planning table
        "cover": "photo-1586528116311-ad8dd3c8310d", # warehouse cover cover
        "logo": "photo-1516321318423-f06f85e504b3" # speed navigation arrow logo
    },
    "fashion": {
        "hero_desktop": "photo-1490481651871-ab68de25d43d", # elegant editorial model banner
        "hero_mobile": "photo-1496747611176-843222e1e57c", # African print fashion wrapper vertical
        "about": "photo-1539109136881-3be0616acf4b", # premium designer workshop
        "product_1": "photo-1539109136881-3be0616acf4b", # tailored Kente modern blazer
        "product_2": "photo-1490481651871-ab68de25d43d", # linen casual corporate kaftan
        "product_3": "photo-1496747611176-843222e1e57c", # traditional wedding wrap wrappers
        "product_4": "photo-1515886657613-9f3515b0c78f", # Ankara printed maxi dress
        "product_5": "photo-1509631179647-0177331693ae", # Ankara prints scarf accessories
        "product_6": "photo-1544816155-12df9643f363", # local handmade leather bag
        "gallery_1": "photo-1539109136881-3be0616acf4b", # tailor fabric rolls
        "gallery_2": "photo-1490481651871-ab68de25d43d", # runway clothing showcase
        "gallery_3": "photo-1496747611176-843222e1e57c", # woven textile prints
        "team_1": "photo-1534528741775-53994a69daeb", # Creative Designer
        "team_2": "photo-1544005313-94ddf0286df2", # Senior Tailor
        "team_3": "photo-1494790108377-be9c29b29330", # Fashion Stylist
        "testimonial_1": "photo-1506794778202-cad84cf45f1d",
        "testimonial_2": "photo-1507003211169-0a1dd7228f2d",
        "testimonial_3": "photo-1500648767791-00dcc994a43e",
        "contact": "photo-1539109136881-3be0616acf4b", # atelier workshop entrance
        "cta": "photo-1490481651871-ab68de25d43d", # custom client layout brief
        "cover": "photo-1539109136881-3be0616acf4b", # textile weaving wrap cover
        "logo": "photo-1509631179647-0177331693ae" # custom dress pattern logo
    },
    "real-estate": {
        "hero_desktop": "photo-1600585154340-be6161a56a0c", # modern premium residential house villa
        "hero_mobile": "photo-1600607687939-ce8a6c25118c", # residential lobby lounge vertical
        "about": "photo-1560518883-ce09059eeffa", # real estate agent holding keys
        "product_1": "photo-1512917774080-9991f1c4c750", # luxury Cantonments apartment blocks
        "product_2": "photo-1600585154340-be6161a56a0c", # gated East Legon villa
        "product_3": "photo-1500382017468-9049fed747ef", # serviced demarcated plots Prampram
        "product_4": "photo-1486406146926-c627a92ad1ab", # Airport City commercial office lease
        "product_5": "photo-1600607687939-ce8a6c25118c", # modern kitchen styling interior
        "product_6": "photo-1600596542815-ffad4c1539a9", # residential villa swimming pool
        "gallery_1": "photo-1600585154340-be6161a56a0c", # estate lawn front
        "gallery_2": "photo-1600607687939-ce8a6c25118c", # luxury living lounge
        "gallery_3": "photo-1600596542815-ffad4c1539a9", # landscape garden pool
        "team_1": "photo-1560250097-0b93528c311a", # Chief Broker
        "team_2": "photo-1573496359142-b8d87734a5a2", # Property Manager
        "team_3": "photo-1519085360753-af0119f7cbe7", # Real Estate Lawyer
        "testimonial_1": "photo-1534528741775-53994a69daeb",
        "testimonial_2": "photo-1507003211169-0a1dd7228f2d",
        "testimonial_3": "photo-1494790108377-be9c29b29330",
        "contact": "photo-1600585154340-be6161a56a0c", # main office building lobby
        "cta": "photo-1560518883-ce09059eeffa", # escrow deed signing briefing
        "cover": "photo-1600585154340-be6161a56a0c", # modern green turf cover
        "logo": "photo-1560518883-ce09059eeffa" # estate roof blueprint logo
    },
    "hospitality-tourism": {
        "hero_desktop": "photo-1507525428034-b723cf961d3e", # tropical resort sand beach getaway
        "hero_mobile": "photo-1545128485-c400e7702796", # Kakum canopy rainforest walk vertical
        "about": "photo-1488646953014-85cb44e25828", # traveler planning route maps
        "product_1": "photo-1507525428034-b723cf961d3e", # Elmina castles heritage group trip
        "product_2": "photo-1545128485-c400e7702796", # Kakum national park canopy walk
        "product_3": "photo-1519494026892-80bbd2d6fd0d", # Mole national park elephant safari
        "product_4": "photo-1539635278303-d4002c07eae3", # luxury oceanfront beach lodge
        "product_5": "photo-1527631746610-bca00a040d60", # Wli waterfalls cascade daytrip
        "product_6": "photo-1501854140801-50d01698950b", # nature eco mountains guide
        "gallery_1": "photo-1507525428034-b723cf961d3e", # ocean shoreline waves
        "gallery_2": "photo-1545128485-c400e7702796", # rainforest canopy bridge
        "gallery_3": "photo-1488646953014-85cb44e25828", # castle historic stone walls
        "team_1": "photo-1560250097-0b93528c311a", # Operations Director
        "team_2": "photo-1519085360753-af0119f7cbe7", # Wildlife Ranger Guide
        "team_3": "photo-1573496359142-b8d87734a5a2", # Cultural Tour Host
        "testimonial_1": "photo-1534528741775-53994a69daeb",
        "testimonial_2": "photo-1507003211169-0a1dd7228f2d",
        "testimonial_3": "photo-1494790108377-be9c29b29330",
        "contact": "photo-1507525428034-b723cf961d3e", # resort check-in lobby desk
        "cta": "photo-1488646953014-85cb44e25828", # booking advisory consultation
        "cover": "photo-1507525428034-b723cf961d3e", # beach ocean sunset cover
        "logo": "photo-1488646953014-85cb44e25828" # travel compass maps logo
    },
    "agriculture": {
        "hero_desktop": "photo-1523741543316-beb7fc7023d8", # sunlit sustainable farm crops rows
        "hero_mobile": "photo-1595974482597-4b8da8879bc5", # tomato harvest crop farm vertical
        "about": "photo-1500937386664-56d1dfef3854", # organic farmers compost harvest
        "product_1": "photo-1599599810769-bcde5a160d32", # wholesale maize grain bags
        "product_2": "photo-1595974482597-4b8da8879bc5", # organic poultry feed grains
        "product_3": "photo-1500937386664-56d1dfef3854", # fresh organic plantain bunches
        "product_4": "photo-1523741543316-beb7fc7023d8", # soil agronomy test consulting
        "product_5": "photo-1592417817098-8f3d6be19aee", # fresh tomato yields boxes
        "product_6": "photo-1505253716362-afaea1d3d1af", # grocery organic produce basket
        "gallery_1": "photo-1523741543316-beb7fc7023d8", # green farm field valleys
        "gallery_2": "photo-1595974482597-4b8da8879bc5", # farm tractor grading land
        "gallery_3": "photo-1500937386664-56d1dfef3854", # local organic harvest crop
        "team_1": "photo-1560250097-0b93528c311a", # Chief Agronomist
        "team_2": "photo-1519085360753-af0119f7cbe7", # Farm Supervisor
        "team_3": "photo-1573496359142-b8d87734a5a2", # Agribusiness Advisor
        "testimonial_1": "photo-1534528741775-53994a69daeb",
        "testimonial_2": "photo-1507003211169-0a1dd7228f2d",
        "testimonial_3": "photo-1494790108377-be9c29b29330",
        "contact": "photo-1582533561751-ef6f6ab93a2e", # farm depot offices entry
        "cta": "photo-1500937386664-56d1dfef3854", # wholesale buyer trade brief
        "cover": "photo-1523741543316-beb7fc7023d8", # farm crops rows cover
        "logo": "photo-1595974482597-4b8da8879bc5" # farm wheat ears crest logo
    },
    "corporate-services": {
        "hero_desktop": "photo-1454165804606-c3d57bc86b40", # corporate leaders strategy workspace
        "hero_mobile": "photo-1551836022-d5d88e9218df", # executive presenter speaking vertical
        "about": "photo-1522071820081-009f0129c71c", # corporate accountants audit desk
        "product_1": "photo-1486406146926-c627a92ad1ab", # business registration documentation
        "product_2": "photo-1554224155-8d04cb21cd6c", # tax compliance audit filing
        "product_3": "photo-1521791136366-3e283b6f007c", # HR outsourcing staffing panel
        "product_4": "photo-1460925895917-afdab827c52f", # digital workflow optimization charts
        "product_5": "photo-1551836022-d5d88e9218df", # strategy pivot blueprint
        "product_6": "photo-1454165804606-c3d57bc86b40", # executive leadership briefing
        "gallery_1": "photo-1486406146926-c627a92ad1ab", # high-rise office towers block
        "gallery_2": "photo-1522071820081-009f0129c71c", # brainstorming workspace dashboard
        "gallery_3": "photo-1454165804606-c3d57bc86b40", # boardroom team workspace presentation
        "team_1": "photo-1560250097-0b93528c311a", # Managing Partner
        "team_2": "photo-1573496359142-b8d87734a5a2", # HR Director
        "team_3": "photo-1519085360753-af0119f7cbe7", # Chief Tax Attorney
        "testimonial_1": "photo-1534528741775-53994a69daeb",
        "testimonial_2": "photo-1507003211169-0a1dd7228f2d",
        "testimonial_3": "photo-1494790108377-be9c29b29330",
        "contact": "photo-1582533561751-ef6f6ab93a2e", # Ridge corporate entry
        "cta": "photo-1522071820081-009f0129c71c", # operations diagnostic audit briefing
        "cover": "photo-1454165804606-c3d57bc86b40", # widescreen boardroom chairs cover
        "logo": "photo-1516321318423-f06f85e504b3" # consultant crest badge logo
    },
    "nonprofit-ngo": {
        "hero_desktop": "photo-1488521787991-ed7bbaae773c", # authentic community program classroom learning
        "hero_mobile": "photo-1509099836639-18ba1795216d", # volunteer sharing drinking water vertical
        "about": "photo-1509099836639-18ba1795216d", # free village health clinic checkups
        "product_1": "photo-1594708767791-00dcc994a43e", # drilled water wells borehole installation
        "product_2": "photo-1509062522246-3755977927d7", # rural library textbooks donation
        "product_3": "photo-1584308666744-24d5c474f2ae", # prenatal health screening kits
        "product_4": "photo-1523741543316-beb7fc7023d8", # crop seeds microloans for women
        "product_5": "photo-1488521787991-ed7bbaae773c", # youth vocational scholarships guidance
        "product_6": "photo-1509062522246-3755977927d7", # village school infrastructure repair
        "gallery_1": "photo-1488521787991-ed7bbaae773c", # community outreach group
        "gallery_2": "photo-1509062522246-3755977927d7", # primary students classes
        "gallery_3": "photo-1509099836639-18ba1795216d", # borehole water well celebration
        "team_1": "photo-1560250097-0b93528c311a", # Foundation President
        "team_2": "photo-1573496359142-b8d87734a5a2", # Programs Director
        "team_3": "photo-1519085360753-af0119f7cbe7", # Outreach Coordinator
        "testimonial_1": "photo-1534528741775-53994a69daeb",
        "testimonial_2": "photo-1507003211169-0a1dd7228f2d",
        "testimonial_3": "photo-1494790108377-be9c29b29330",
        "contact": "photo-1582533561751-ef6f6ab93a2e", # Kanda charity offices
        "cta": "photo-1509099836639-18ba1795216d", # volunteer intake orientation
        "cover": "photo-1488521787991-ed7bbaae773c", # smiling sunlit children banner cover
        "logo": "photo-1509099836639-18ba1795216d" # hope bridge heart logo
    },
    "default": {
        "hero_desktop": "photo-1497366216548-37526070297c", # clean modern geometric office workspace
        "hero_mobile": "photo-1497215728101-856f4ea42174", # lobby workspace vertical
        "about": "photo-1497366811353-6870744d04b2", # modern design workspace outline
        "product_1": "photo-1497366216548-37526070297c", # component detail border block
        "product_2": "photo-1516321318423-f06f85e504b3", # dynamic tool preview card
        "product_3": "photo-1522071820081-009f0129c71c", # team review component
        "product_4": "photo-1486406146926-c627a92ad1ab", # contrast border test card
        "product_5": "photo-1551288049-bebda4e38f71", # analytics mockup board
        "product_6": "photo-1563986768609-322da13575f3", # security badge review
        "gallery_1": "photo-1497215728101-856f4ea42174", # lobby workspace overview
        "gallery_2": "photo-1497366216548-37526070297c", # general workspace mockup
        "gallery_3": "photo-1497366811353-6870744d04b2", # workspace strategy board
        "team_1": "photo-1560250097-0b93528c311a",
        "team_2": "photo-1573496359142-b8d87734a5a2",
        "team_3": "photo-1519085360753-af0119f7cbe7",
        "testimonial_1": "photo-1534528741775-53994a69daeb",
        "testimonial_2": "photo-1507003211169-0a1dd7228f2d",
        "testimonial_3": "photo-1494790108377-be9c29b29330",
        "contact": "photo-1582533561751-ef6f6ab93a2e", # corporate offices entry
        "cta": "photo-1522071820081-009f0129c71c", # strategy consulting outline
        "cover": "photo-1497366216548-37526070297c", # workspace line grid cover
        "logo": "photo-1516321318423-f06f85e504b3" # general brand emblem logo
    }
}

def create_fallback_image(filepath, category, image_key, width, height):
    """
    Creates a highly styled category-specific colored image using Pillow
    if the network download fails.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    img = Image.new("RGB", (width, height), color="#f1f5f9")
    draw = ImageDraw.Draw(img)
    
    # Draw simple professional geometric layout
    draw.rectangle([0, 0, width, height], fill="#1e293b")
    # Draw border
    draw.rectangle([10, 10, width - 10, height - 10], outline="#f59e0b", width=2)
    # Draw some abstract circles
    draw.ellipse([width // 2 - 100, height // 2 - 100, width // 2 + 100, height // 2 + 100], outline="#2563eb", width=4)
    draw.line([0, 0, width, height], fill="#64748b", width=1)
    
    # Text info
    info_text = f"{category.upper()} - {image_key.upper()}\n({width}x{height})"
    draw.text((20, 20), info_text, fill="#f8fafc")
    
    img.save(filepath, "WEBP", quality=80)
    print(f"  Created Pillow fallback image: {filepath}")

def main():
    print("Starting Premium Preview Images Acquisition System...")
    
    # Create static previews base dir
    os.makedirs(PREVIEWS_DIR, exist_ok=True)
    
    # Create the shared & fallback dirs if needed
    os.makedirs(os.path.join(PREVIEWS_DIR, "shared"), exist_ok=True)
    os.makedirs(os.path.join(PREVIEWS_DIR, "fallback"), exist_ok=True)
    
    total_downloaded = 0
    total_failed = 0
    start_time = time.time()
    
    for category_slug, img_map in UNSPLASH_IDS.items():
        folder_name = CATEGORY_FOLDER_MAP.get(category_slug)
        if not folder_name:
            continue
            
        target_folder = os.path.join(PREVIEWS_DIR, folder_name)
        os.makedirs(target_folder, exist_ok=True)
        
        print(f"\nProcessing category: '{category_slug}' -> folder: '{folder_name}'...")
        
        for image_key, photo_id in img_map.items():
            width, height = IMAGE_DIMENSIONS.get(image_key, (800, 600))
            quality = TARGET_QUALITY.get(image_key, 80)
            
            # Local output filename
            filename = f"{image_key}.webp"
            filepath = os.path.join(target_folder, filename)
            
            # Construct Unsplash source URL with exact sizes
            url = f"https://images.unsplash.com/{photo_id}?auto=format&fit=crop&w={width}&h={height}&q={quality}"
            
            print(f" - Downloading {image_key} ({width}x{height}) ID: {photo_id}...")
            
            download_success = False
            for attempt in range(2): # try twice
                try:
                    req = urllib.request.Request(
                        url, 
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                    )
                    with urllib.request.urlopen(req, timeout=12) as response:
                        img_data = response.read()
                        
                    # Process image with Pillow
                    with Image.open(io.BytesIO(img_data)) as img:
                        # Make sure it's RGB
                        if img.mode != "RGB":
                            img = img.convert("RGB")
                            
                        # Save optimized WebP
                        img.save(filepath, "WEBP", quality=quality)
                        
                    print(f"   Successfully saved WebP: {filepath} ({len(img_data) // 1024} KB)")
                    download_success = True
                    total_downloaded += 1
                    break
                except Exception as e:
                    print(f"   Attempt {attempt + 1} failed: {e}")
                    time.sleep(1)
            
            if not download_success:
                print(f"   Fallback to programmatically generated image for {image_key}...")
                create_fallback_image(filepath, category_slug, image_key, width, height)
                total_failed += 1
                
            # Be polite to the CDN
            time.sleep(0.1)
            
    # Also copy default/fallback/general-business.webp to previews/fallback/general-business.webp
    # and save some shared icons/patterns under Shared folder
    fallback_business_path = os.path.join(PREVIEWS_DIR, "fallback", "business-placeholder.webp")
    if not os.path.exists(fallback_business_path):
        create_fallback_image(fallback_business_path, "shared", "business-placeholder", 1200, 700)
        
    print("\n==================================================")
    print(f"Completed Image Acquisition: {total_downloaded} downloaded, {total_failed} generated fallbacks.")
    print(f"Total time elapsed: {time.time() - start_time:.2f} seconds.")
    print("==================================================")

if __name__ == "__main__":
    main()

