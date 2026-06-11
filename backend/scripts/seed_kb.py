"""Generate Saksham knowledge base seed topic files."""

import json
from pathlib import Path

KB_DIR = Path(__file__).resolve().parent.parent / "data" / "saksham_kb"

TOPICS = {
    "Science": {
        "Food and Nutrition": "Food provides energy and nutrients for growth. Carbohydrates give energy, proteins build muscles, fats store energy, vitamins and minerals keep the body healthy. A balanced diet includes fruits, vegetables, grains, and proteins. Malnutrition occurs when the body lacks essential nutrients.",
        "Living and Non-living Things": "Living things grow, reproduce, respond to stimuli, and need food and water. Plants make food through photosynthesis. Animals depend on plants or other animals for food. Non-living things do not grow, breathe, or reproduce. Examples include rocks, water, and air.",
        "Components of Food": "Our food contains carbohydrates, proteins, fats, vitamins, and minerals. Carbohydrates are found in rice and bread. Proteins in pulses and eggs build body tissues. Fats provide stored energy. Vitamins prevent diseases. Minerals like calcium strengthen bones.",
        "Fibre to Fabric": "Fibres are thin threads obtained from plants like cotton and jute, or animals like sheep and silkworms. Cotton is grown in fields and spun into yarn. Weaving interlaces yarns to make fabric. Knitting uses a single yarn. Natural fibres are biodegradable and eco-friendly.",
        "Separation of Substances": "Mixtures contain two or more substances. Handpicking removes visible impurities. Winnowing separates lighter husk from heavier grains using wind. Sieving uses a mesh to filter particles by size. Evaporation separates dissolved solids from liquids by heating.",
    },
    "Mathematics": {
        "Knowing Our Numbers": "Large numbers are read using place value: ones, tens, hundreds, thousands, lakhs, and crores. Comparing numbers uses greater than and less than symbols. Estimation rounds numbers for quick calculation. Roman numerals use letters I, V, X, L, C, D, M to represent values.",
        "Whole Numbers": "Whole numbers start from zero and include all natural numbers. The number line helps visualize addition and subtraction. Zero is the identity for addition. Commutative property: a plus b equals b plus a. Associative property groups numbers differently without changing the result.",
        "Basic Geometrical Ideas": "A point has no size, a line extends endlessly in both directions, and a line segment has two endpoints. An angle is formed when two rays meet. Triangles have three sides. Circles have a centre and radius. Parallel lines never meet. Perpendicular lines meet at ninety degrees.",
        "Integers": "Integers include positive numbers, negative numbers, and zero. On the number line, numbers increase to the right. Adding a negative is like moving left. Subtracting a negative equals adding its positive. Absolute value is the distance from zero without sign.",
        "Data Handling": "Data is collected information. A pictograph uses pictures to represent data. A bar graph uses bars of different heights. The mean is the average found by dividing the sum by count. The mode is the most frequent value. Organizing data helps find patterns.",
    },
}

CLASS_TOPICS = {
    6: {
        "Science": ["Food and Nutrition", "Living and Non-living Things", "Components of Food", "Fibre to Fabric", "Separation of Substances"],
        "Mathematics": ["Knowing Our Numbers", "Whole Numbers", "Basic Geometrical Ideas", "Integers", "Data Handling"],
    },
    7: {
        "Science": ["Nutrition in Plants", "Nutrition in Animals", "Heat", "Acids Bases and Salts", "Physical and Chemical Changes"],
        "Mathematics": ["Integers", "Fractions and Decimals", "Data Handling", "Simple Equations", "Lines and Angles"],
    },
    8: {
        "Science": ["Crop Production", "Microorganisms", "Force and Pressure", "Friction", "Sound"],
        "Mathematics": ["Rational Numbers", "Linear Equations", "Understanding Quadrilaterals", "Squares and Square Roots", "Exponents and Powers"],
    },
    9: {
        "Science": ["Matter in Our Surroundings", "Is Matter Around Us Pure", "Atoms and Molecules", "Motion", "Force and Laws of Motion"],
        "Mathematics": ["Number Systems", "Polynomials", "Coordinate Geometry", "Linear Equations in Two Variables", "Statistics"],
    },
    10: {
        "Science": ["Chemical Reactions", "Acids Bases and Salts", "Life Processes", "Light Reflection and Refraction", "Electricity"],
        "Mathematics": ["Real Numbers", "Polynomials", "Pair of Linear Equations", "Quadratic Equations", "Arithmetic Progressions"],
    },
}

CONTENT = {
    ("Nutrition in Plants", 7): "Plants make their own food through photosynthesis using sunlight, water, and carbon dioxide. Chlorophyll in leaves captures sunlight. Stomata allow gas exchange. Plants also absorb minerals from soil through roots. Nitrogen-fixing bacteria help leguminous plants. Saprotrophs like fungi feed on dead organic matter.",
    ("Nutrition in Animals", 7): "Animals obtain food from plants or other animals. Digestion breaks food into absorbable nutrients. The human digestive system includes mouth, oesophagus, stomach, small intestine, and large intestine. Enzymes speed up digestion. Absorption occurs mainly in the small intestine. Assimilation uses nutrients for growth and repair.",
    ("Heat", 7): "Heat flows from hotter to colder objects until temperatures equalize. Thermometers measure temperature in Celsius or Fahrenheit. Conduction transfers heat through solids. Convection occurs in fluids. Radiation needs no medium. Good conductors like metals transfer heat quickly. Insulators like wood reduce heat flow.",
    ("Acids Bases and Salts", 7): "Acids taste sour and turn blue litmus red. Bases taste bitter and turn red litmus blue. The pH scale measures acidity from zero to fourteen. Neutral substances have pH seven. Indicators like turmeric and china rose detect acids and bases. Neutralization produces salt and water.",
    ("Physical and Chemical Changes", 7): "Physical changes alter appearance but not composition, like melting ice. Chemical changes form new substances, like rusting iron. Burning is a chemical change producing ash and gases. Crystallization is physical. Photosynthesis is chemical. Reversible physical changes can be undone; most chemical changes cannot.",
    ("Fractions and Decimals", 7): "Fractions represent parts of a whole. Equivalent fractions have the same value. Adding fractions needs a common denominator. Decimals are fractions with denominators of ten. Converting fractions to decimals uses division. Percentages express parts per hundred.",
    ("Simple Equations", 7): "An equation states two expressions are equal. Solving finds the unknown variable. Add or subtract the same value on both sides to isolate the variable. Multiplication and division follow the same rule. Word problems translate real situations into equations.",
    ("Lines and Angles", 7): "A line segment has two endpoints. A ray has one endpoint. Angles measure rotation between rays. Complementary angles sum to ninety degrees. Supplementary angles sum to one hundred eighty degrees. Vertically opposite angles are equal. Transversal lines create corresponding and alternate angles.",
    ("Crop Production", 8): "Agriculture provides food and raw materials. Crop preparation includes tilling, sowing, and irrigation. Manure and fertilizers improve soil fertility. Crop rotation maintains soil nutrients. Pesticides protect crops from pests. Harvesting collects mature crops. Storage prevents spoilage.",
    ("Microorganisms", 8): "Microorganisms include bacteria, fungi, protozoa, and viruses. Some cause diseases while others are beneficial. Yeast ferments bread and produces alcohol. Bacteria in curd formation are useful. Vaccines prevent viral diseases. Antibiotics treat bacterial infections. Pasteurization kills harmful microbes in milk.",
    ("Force and Pressure", 8): "Force is a push or pull that can change motion or shape. Force is measured in newtons. Pressure equals force divided by area. Smaller area creates greater pressure. Friction opposes motion. Gravitational force pulls objects toward Earth. Magnetic force acts at a distance.",
    ("Friction", 8): "Friction opposes relative motion between surfaces in contact. Static friction prevents motion. Sliding friction acts during movement. Rolling friction is less than sliding friction. Friction enables walking and driving. Lubricants reduce friction. Excessive friction causes wear and generates heat.",
    ("Sound", 8): "Sound is produced by vibrating objects. It travels through solids, liquids, and gases as waves. Frequency determines pitch. Amplitude determines loudness. The human ear detects sound vibrations. Echo is reflected sound. Sound cannot travel through vacuum. Speed of sound is fastest in solids.",
    ("Rational Numbers", 8): "Rational numbers can be written as p over q where q is not zero. They include integers and fractions. Rational numbers are closed under addition, subtraction, multiplication, and division. Every rational number has a decimal expansion that terminates or repeats. They can be represented on the number line.",
    ("Linear Equations", 8): "A linear equation in one variable has the highest power one. Solving involves isolating the variable. Linear equations model real-world problems like age and money. Graphs of linear equations in two variables form straight lines. Solutions satisfy the equation when substituted.",
    ("Understanding Quadrilaterals", 8): "A quadrilateral has four sides and four angles. Sum of interior angles is three hundred sixty degrees. Parallelograms have opposite sides parallel and equal. Rectangles have right angles. Rhombus has equal sides. Trapezium has one pair of parallel sides. Square combines rectangle and rhombus properties.",
    ("Squares and Square Roots", 8): "Squaring a number multiplies it by itself. Perfect squares are one, four, nine, sixteen, and so on. Square root is the inverse of squaring. The square root of a perfect square is a whole number. Pythagoras theorem relates sides of a right triangle.",
    ("Exponents and Powers", 8): "Exponents show repeated multiplication. Ten to the power three equals one thousand. Laws of exponents simplify calculations. Negative exponents represent reciprocals. Scientific notation expresses very large or small numbers. Any number to power zero equals one.",
    ("Matter in Our Surroundings", 9): "Matter occupies space and has mass. Three states are solid, liquid, and gas. Particles in matter are constantly moving. Temperature affects particle motion. Evaporation occurs at any temperature at the surface. Condensation is gas to liquid. Sublimation is solid to gas directly.",
    ("Is Matter Around Us Pure", 9): "Pure substances have fixed composition. Mixtures contain two or more substances. Solutions are homogeneous mixtures. Suspensions are heterogeneous. Colloids show Tyndall effect. Separation techniques include filtration, distillation, and chromatography. Elements and compounds are pure substances.",
    ("Atoms and Molecules", 9): "Atoms are the smallest units of elements. Molecules are groups of atoms bonded together. Atomic mass unit measures atomic mass. Avogadro number relates moles to particles. Chemical formulas show element ratios. Law of conservation of mass applies to reactions.",
    ("Motion", 9): "Motion is change in position over time. Distance is total path length. Displacement is shortest distance with direction. Speed is distance over time. Velocity includes direction. Acceleration is rate of change of velocity. Uniform motion has constant velocity.",
    ("Force and Laws of Motion", 9): "Newton's first law: objects at rest stay at rest unless acted upon. Second law: force equals mass times acceleration. Third law: every action has equal and opposite reaction. Momentum is mass times velocity. Impulse changes momentum. Friction affects motion.",
    ("Number Systems", 9): "Real numbers include rational and irrational numbers. Irrational numbers like root two cannot be expressed as fractions. Their decimal expansions are non-terminating and non-repeating. Number line represents all real numbers. Operations on irrationals may produce rationals or irrationals.",
    ("Polynomials", 9): "Polynomials are expressions with variables and coefficients. Degree is the highest power of the variable. Zero polynomial has degree undefined. Factor theorem relates factors and zeros. Remainder theorem finds remainder without division. Algebraic identities simplify expansion.",
    ("Coordinate Geometry", 9): "The Cartesian plane has x and y axes. Coordinates locate points as ordered pairs. Distance formula finds distance between two points. Section formula divides a line segment in a ratio. Area of triangle uses coordinates. Origin is point zero comma zero.",
    ("Linear Equations in Two Variables", 9): "Equations like ax plus by plus c equals zero have infinitely many solutions. Graphs are straight lines. A system of two equations may have unique, infinite, or no solutions. Substitution and elimination methods solve systems. Applications include age and mixture problems.",
    ("Statistics", 9): "Statistics organizes and analyzes data. Mean, median, and mode are measures of central tendency. Range measures spread. Frequency distribution groups data. Histograms display grouped data. Probability measures likelihood of events. Experimental probability uses observed outcomes.",
    ("Chemical Reactions", 10): "Chemical reactions rearrange atoms to form new substances. Reactants transform into products. Combination reactions merge substances. Decomposition breaks compounds apart. Displacement replaces one element with another. Oxidation involves loss of electrons. Reduction involves gain of electrons.",
    ("Life Processes", 10): "Life processes include nutrition, respiration, transport, excretion, and reproduction. Autotrophs make food; heterotrophs consume it. Aerobic respiration uses oxygen. Circulatory system transports blood. Excretion removes waste. Coordination uses nervous and hormonal systems.",
    ("Light Reflection and Refraction", 10): "Light travels in straight lines. Reflection bounces light off surfaces. Laws of reflection: angle of incidence equals angle of reflection. Refraction bends light passing between media. Lenses converge or diverge light. Human eye uses lens to focus images on retina.",
    ("Electricity", 10): "Electric current is flow of charge. Voltage drives current. Resistance opposes current flow. Ohm's law: V equals I times R. Series circuits have single path. Parallel circuits have multiple paths. Electrical power equals voltage times current.",
    ("Real Numbers", 10): "Real numbers include all rational and irrational numbers. Euclid's division lemma relates dividend, divisor, quotient, and remainder. Fundamental theorem of arithmetic states unique prime factorization. HCF and LCM use prime factorization. Irrationality of root two proved by contradiction.",
    ("Pair of Linear Equations", 10): "Two linear equations in two variables form a system. Graphical method plots both lines. Algebraic methods include substitution and elimination. Consistent systems have at least one solution. Inconsistent systems have no solution. Dependent systems have infinite solutions.",
    ("Quadratic Equations", 10): "Quadratic equations have form ax squared plus bx plus c equals zero. Solutions found by factorization or quadratic formula. Discriminant b squared minus four ac determines nature of roots. Sum and product of roots relate to coefficients. Applications include area and motion problems.",
    ("Arithmetic Progressions", 10): "An AP has constant difference between consecutive terms. nth term equals a plus n minus one times d. Sum of n terms equals n over two times two a plus n minus one d. AP models patterns like savings and seating arrangements. Common difference can be positive or negative.",
}


def get_content(class_level: int, subject: str, topic: str) -> str:
    """Return content for a topic, using class-specific or default content."""
    key = (topic, class_level)
    if key in CONTENT:
        return CONTENT[key]
    if topic in TOPICS.get(subject, {}):
        return TOPICS[subject][topic]
    return f"This topic covers {topic} for Class {class_level} {subject} students. It includes fundamental concepts, definitions, examples, and practice applications aligned with the curriculum."


def main() -> None:
    """Generate all 50 topic JSON files."""
    count = 0
    for class_level, subjects in CLASS_TOPICS.items():
        for subject, topics in subjects.items():
            subject_dir = KB_DIR / f"class{class_level}" / subject.lower().replace(" ", "_")
            subject_dir.mkdir(parents=True, exist_ok=True)
            for topic in topics:
                data = {
                    "class": class_level,
                    "subject": subject,
                    "topic": topic,
                    "content": get_content(class_level, subject, topic),
                }
                filename = topic.lower().replace(" ", "_").replace(",", "") + ".json"
                filepath = subject_dir / filename
                filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
                count += 1
    print(f"Generated {count} topic files in {KB_DIR}")


if __name__ == "__main__":
    main()
