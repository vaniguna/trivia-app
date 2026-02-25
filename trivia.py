import streamlit as st
import pandas as pd
import random
import glob
import re
import os
import hashlib
from drill_mode import render_drill_mode

st.set_page_config(page_title="Jeopardy! Pro Trainer", page_icon="🎓", layout="centered")

# --- 1. STUDY TAG ENGINE ---
# Tags are ordered from most specific to most general within each pass.
# The first match wins, so specific tags (Shakespeare) must come before
# their parent (Literature) to avoid being swallowed.

# PASS 1: Match against the Jeopardy category string only.
CATEGORY_MAP = {

    # ── HISTORY ──────────────────────────────────────────────────────────────
    "U.S. Presidents":          r"president|first lad(y|ies)|oval office|commander.in.chief",
    "American Revolution":      r"revolutionary war|founding father|colonial america|declaration of independence|continental congress|patriot|loyalist|lexington|yorktown|saratoga",
    "U.S. Civil War":           r"civil war|confedera|union army|gettysburg|lincoln.*war|reconstruction|emancipation",
    "20th Century U.S. History":r"20th century.*u\.?s|american.*20th|new deal|great depression|vietnam.*war|watergate|cold war.*amer|korean war",
    "American History":         r"american history|u\.?s\.? history|us history|westward|manifest destiny|lewis.*clark|gold rush|prohibition|suffrage|civil rights",
    "Ancient History":          r"ancient (rome|greece|egypt|china|mesopotamia|persia|civiliz)|roman empire|greek empire|pharaoh|julius caesar|alexander the great|classical antiquity",
    "Medieval History":         r"medieval|middle ages|feudal|crusade|knight|castle|magna carta|black death|plague|viking|norman|byzantine",
    "European History":         r"european history|french revolution|napoleon|renaissance.*europe|hapsburg|bourbon|tudor|stuart|romanov|otto.*bismarck|weimar|austro",
    "World War I":              r"world war i\b|world war 1\b|wwi\b|great war|western front|trench warfare|versailles|archduke|gallipoli",
    "World War II":             r"world war ii\b|world war 2\b|wwii\b|nazi|holocaust|d.day|hiroshima|nagasaki|pearl harbor|normandy|allies.*axis",
    "Cold War":                 r"cold war|soviet union|ussr|iron curtain|berlin wall|cuban missile|space race|khrushchev|reagan.*soviet|nato.*warsaw",
    "World History":            r"world history|history of the world|ancient history|dynasty|empire|revolution|colonialism|imperialism|independence.*movement",
    "African History":          r"african history|africa.*history|apartheid|nelson mandela|saharan|zulu|mali empire|songhai|slave trade.*africa",
    "Asian History":            r"asian history|china.*history|japan.*history|mao|meiji|qing|ming dynasty|shogun|samurai|mughal|partition.*india",
    "Latin American History":   r"latin american|south american history|mexican history|simón bolívar|conquistador|aztec|inca|maya|fidel castro|che guevara",

    # ── GEOGRAPHY ────────────────────────────────────────────────────────────
    "World Capitals":           r"world capital|capital cit|capital of (the|a )",
    "U.S. States & Cities":     r"u\.?s\.? state|state capital|american cit|american state|u\.?s\.? cit|u\.?s\.? geography|50 state",
    "African Geography":        r"africa.*geograph|african countr|african capital|african river|african mountain|sahara|sub.saharan",
    "Asian Geography":          r"asia.*geograph|asian countr|asian capital|asian river|himalaya|gobi|yangtze|mekong|ganges",
    "European Geography":       r"europe.*geograph|european countr|european capital|european river|alps|rhine|danube|thames",
    "World Geography":          r"geograph|countr|nation|continent|river|mountain|lake|ocean|sea|island|peninsula|border|flag|map|latitude|longitude|hemisphere",

    # ── SCIENCE ──────────────────────────────────────────────────────────────
    "Astronomy & Space":        r"astronom|space|planet|star|comet|asteroid|galaxy|cosmos|nasa|telescope|solar system|nebula|orbit|black hole|constellation",
    "Biology":                  r"biolog|species|evolution|dna|rna|gene|cell|ecosystem|taxonomy|mammal|vertebrate|invertebrate|microb|bacteri|virus|fungi",
    "Chemistry":                r"chemistr|element|periodic table|compound|molecule|atom|bond|reaction|acid|base|polymer|isotope|valence|oxidat",
    "Physics":                  r"physic|force|energy|gravity|quantum|relativity|newton|einstein|thermodynamic|electro|magnet|wave|particle|velocity|momentum",
    "Earth Science":            r"earth science|geology|geograph.*science|volcano|earthquake|tectonic|mineral|rock|fossil|erosion|atmosphere|ocean.*science|meteorolog|climate science",
    "Human Body & Medicine":    r"human body|anatomy|physiology|medicine|medical|disease|organ|muscle|bone|nerve|brain|heart|lung|blood|surgery|diagnosis|symptom|syndrome|doctor|physician",
    "Science & Nature":         r"science|nature|natural world|wildlife|environment|ecology|animal|plant|botany|zoology|weather|climate|insect|reptile|amphibian",

    # ── MATHEMATICS ──────────────────────────────────────────────────────────
    "Mathematics":              r"math|algebra|geometry|calculus|equation|number theory|fraction|prime|theorem|statistic|probabilit|trigonometr|logarithm|matrix|vector",

    # ── LITERATURE ───────────────────────────────────────────────────────────
    "Shakespeare":              r"shakespeare|bard of avon|hamlet|macbeth|othello|king lear|midsummer|the tempest|romeo.*juliet|merchant of venice|much ado",
    "American Literature":      r"american literature|american novel|american author|american poet|twain|hemingway|fitzgerald|steinbeck|faulkner|whitman|dickinson|poe|hawthorne|melville|updike|morrison",
    "British Literature":       r"british literature|english literature|english novel|british author|dickens|austen|bronte|hardy|orwell|woolf|kipling|chaucer|milton|keats|shelley|byron|tennyson",
    "Classic Literature":       r"classic(al)? literature|classic novel|great books|literary classic|homer|dante|cervantes|tolstoy|dostoevsky|kafka|proust|joyce|chekhov",
    "Poetry":                   r"\bpoetry\b|\bpoem\b|\bpoets?\b|\bsonnet\b|\bode\b|\bverse\b|\blyric\b.*poet|laureate|pulitzer.*poem|epic poem",
    "Children's Literature":    r"children.s (book|literature|story|fiction)|fairy tale|nursery rhyme|dr\. seuss|roald dahl|beatrix potter|grimm|andersen",
    "Literature":               r"literature|novel|author|fiction|nonfiction|book|pulitzer|short stor|playwright|narrator|chapter|character.*novel",

    # ── ARTS ─────────────────────────────────────────────────────────────────
    "Classical Music":          r"classical music|composer|symphony|concerto|sonata|opera|orchestra|beethoven|mozart|bach|chopin|brahms|handel|vivaldi|schubert|liszt",
    "Jazz & Blues":             r"jazz|blues|ragtime|bebop|swing music|louis armstrong|miles davis|john coltrane|duke ellington|billie holiday|muddy waters",
    "Rock & Pop Music":         r"rock music|pop music|rock.*roll|punk|heavy metal|indie rock|alternative|billboard|grammy.*rock|grammy.*pop|rolling stones|beatles|elvis|bowie|michael jackson",
    "Music":                    r"music|musician|singer|band|album|song|grammy|lyric|melody|chord|rhythm|record label|tour|concert",
    "Painting & Sculpture":     r"painting|sculpture|painter|sculptor|canvas|fresco|mural|watercolor|oil paint|van gogh|picasso|monet|rembrandt|da vinci|michelangelo|rodin|warhol|dali",
    "Architecture":             r"architect|architecture|building|skyscraper|cathedral|monument|landmark|bridge.*design|frank lloyd wright|modernist.*build|gothic.*cathedral",
    "Art & Architecture":       r"\bart\b|artist|museum|gallery|exhibit|aesthetic|impressi|cubis|surreali|abstract|renaissance art|louvre|moma|metropolitan museum",
    "Theater & Dance":          r"theater|theatre|broadway|musical|ballet|dance|choreograph|tony award|stage|opera.*stage|playwright|west end",
    "Fashion & Design":         r"fashion|designer|couture|runway|vogue|haute|clothing|style.*fashion|chanel|dior|gucci|prada|armani",

    # ── FILM & TELEVISION ────────────────────────────────────────────────────
    "Oscar-Winning Films":      r"oscar|academy award|best picture|best director|best actor|best actress|best screenplay",
    "Film Directors":           r"director|filmmaker|auteur|spielberg|scorsese|kubrick|hitchcock|coppola|tarantino|nolan|lynch",
    "Animated Films & TV":      r"animated|cartoon|pixar|disney.*film|dreamworks|anime|studio ghibli|looney tunes|simpson|south park",
    "TV Shows & Series":        r"television|tv show|sitcom|drama series|emmy|streaming|netflix.*show|hbo.*show|series finale|spin.?off",
    "Film & TV":                r"movie|film|cinema|actor|actress|hollywood|box office|screen|blockbuster|sequel|franchise|cameo",

    # ── SPORTS ───────────────────────────────────────────────────────────────
    "American Football":        r"football|nfl|super bowl|quarterback|touchdown|gridiron|linebacker|wide receiver",
    "Baseball":                 r"baseball|mlb|world series|pitcher|batting|home run|yankees|red sox|dodgers",
    "Basketball":               r"basketball|nba|slam dunk|three.pointer|point guard|lebron|michael jordan|nba finals",
    "Soccer / Football":        r"soccer|football.*world cup|fifa|premier league|la liga|bundesliga|serie a|champions league|goalkeeper|striker|penalty",
    "Tennis":                   r"tennis|wimbledon|us open.*tennis|french open|australian open|grand slam.*tennis|serena|federer|nadal|djokovic",
    "Golf":                     r"\bgolf\b|pga|masters.*golf|open championship|birdie|eagle|bogey|fairway|tiger woods",
    "Winter Sports & Olympics":  r"winter olympic|ski|skiing|ice skating|figure skating|hockey|speed skate|luge|bobsled|snowboard",
    "Olympics":                 r"olympic|olympiad|games.*athens|games.*beijing|games.*tokyo|gold medal|silver medal|bronze medal|olympic record",
    "Sports":                   r"sport|athlete|champion|tournament|league|playoff|coach|stadium|trophy|record.*sport|hall of fame.*sport",

    # ── FOOD & DRINK ─────────────────────────────────────────────────────────
    "Wine & Spirits":           r"wine|champagne|whiskey|whisky|bourbon|vodka|gin|rum|brandy|tequila|vineyard|winery|sommelier|vintage.*wine",
    "Food & Drink":             r"food|cuisine|cooking|chef|recipe|ingredient|beverage|dish|restaurant|gastron|flavor|spice|bread|cheese|dessert|cocktail|beer",

    # ── LANGUAGE & WORDS ─────────────────────────────────────────────────────
    "Foreign Languages":        r"french (word|phrase|language)|spanish (word|phrase|language)|german (word|phrase|language)|italian (word|phrase|language)|latin (word|phrase)|japanese (word|phrase)|translate|foreign language",
    "Word Origins & Etymology": r"etymolog|word origin|root word|latin root|greek root|borrowed word|loanword",
    "Wordplay & Puzzles":       r"anagram|palindrome|rhyme|homophone|pun|wordplay|crossword|riddle|acronym|abbreviation|portmanteau",
    "Language & Words":         r"word|words|language|grammar|vocabulary|prefix|suffix|synonym|antonym|verb|noun|adjective|adverb|spelling|definition",

    # ── SOCIAL SCIENCES ──────────────────────────────────────────────────────
    "U.S. Government & Politics":r"u\.?s\.? government|u\.?s\.? politic|congress|senate|supreme court|constitution.*law|bill of rights|electoral|filibuster|amendment|political party",
    "World Politics":           r"world politic|foreign policy|united nations|diplomacy|treaty|nato|european union|international relation|geopolitic|prime minister|chancellor|parliament",
    "Economics":                r"econom|gdp|inflation|recession|stock market|supply.*demand|trade|tariff|fiscal|monetary|keynesian|capitalism|socialism|free market",
    "Psychology":               r"psycholog|behavior|cognit|freud|jung|pavlov|therapy|mental health|personality|neuroscience|cognitive|emotion|motivation",
    "Sociology & Anthropology": r"sociolog|anthropolog|culture|society|social.*structure|ethnograph|demograph|tribe|ritual|custom|norm.*social",

    # ── RELIGION & PHILOSOPHY ────────────────────────────────────────────────
    "The Bible & Christianity": r"bible|biblical|testament|gospel|jesus|christ|christian|church|pope|saint|apostle|psalm|proverb|genesis|exodus|revelation",
    "World Religions":          r"religion|islam|muslim|quran|hinduism|buddhism|judaism|sikhism|taoism|confucian|shinto|mosque|synagogue|temple.*religion",
    "Philosophy":               r"philosoph|ethics|logic|epistemology|metaphysics|plato|aristotle|socrates|kant|descartes|nietzsche|hegel|locke|hume|existential|utilitari",
    "Religion & Philosophy":    r"theology|spiritual|faith|belief|meditation|soul|divine|sacred|myth.*religion",

    # ── MYTHOLOGY ────────────────────────────────────────────────────────────
    "Greek & Roman Mythology":  r"greek myth|roman myth|olympus|zeus|hera|apollo|athena|poseidon|ares|aphrodite|hermes|hercules|odysseus|achilles|jupiter|juno|mars|venus|mercury|neptune",
    "Norse Mythology":          r"norse myth|viking myth|thor|odin|loki|freya|valhalla|asgard|ragnarok|yggdrasil",
    "Mythology":                r"myth|mythology|legend|folklore|fable|deity|pantheon|demigod|hero.*myth|creature.*myth",

    # ── TECHNOLOGY & COMPUTING ───────────────────────────────────────────────
    "Computers & Technology":   r"computer|technology|software|hardware|internet|coding|programming|algorithm|artificial intelligence|ai\b|machine learning|cybersecurity|app|operating system|silicon valley",
    "Inventions & Inventors":   r"invention|inventor|patent|thomas edison|nikola tesla|alexander graham bell|wright brothers|innovati|breakthrough|discover.*invent",

    # ── MISCELLANEOUS ────────────────────────────────────────────────────────
    "Animals & Wildlife":       r"animal|wildlife|mammal|bird|reptile|amphibian|fish|insect|spider|predator|prey|endangered|habitat|species",
    "Plants & Botany":          r"plant|botany|flower|tree|shrub|herb|fungi|mushroom|garden|horticulture|flora|seed|petal|photosynthesis",
    "Holidays & Traditions":    r"holiday|christmas|thanksgiving|halloween|easter|hanukkah|diwali|ramadan|tradition|celebration|festival|new year",
    "Royalty & Nobility":       r"royal|royalty|king|queen|prince|princess|monarch|throne|crown|dynasty.*royal|nobility|duke|earl|count|baron|aristocra",
    "Crime & Law":              r"crime|criminal|law|legal|court|trial|verdict|lawyer|attorney|judge|jury|detective|murder|theft|fraud|forensic",
    "Awards & Honors":          r"award|prize|honor|pulitzer|nobel|emmy|grammy|oscar|tony|golden globe|laureat|recipient.*award",
    "Potpourri":                r"potpourri|hodgepodge|miscellan|grab bag|mix|assorted",
}

# PASS 2: Broader content-based fallback (category + clue text combined).
CONTENT_MAP = {
    "U.S. Presidents":          r"\bpresident\b.*(\bU\.?S\.?\b|american|white house)|white house|potus|\b(lincoln|washington|jefferson|madison|monroe|adams|jackson|polk|taylor|fillmore|pierce|buchanan|grant|hayes|garfield|arthur|cleveland|harrison|mckinley|roosevelt|taft|wilson|harding|coolidge|hoover|truman|eisenhower|kennedy|johnson|nixon|ford|carter|reagan|bush|clinton|obama|trump|biden)\b",
    "American Revolution":      r"revolutionary war|lexington.*concord|bunker hill|valley forge|continental army|thomas paine|common sense.*paine|boston tea party|stamp act",
    "U.S. Civil War":           r"civil war|gettysburg|antietam|bull run|confedera|union.*army|ulysses.*grant|robert e\.? lee|stonewall jackson|emancipation proclamation|underground railroad",
    "20th Century U.S. History":r"new deal|great depression|dust bowl|vietnam war|korean war|watergate|cuban missile|moon landing|martin luther king|civil rights movement|malcolm x|woodstock|women.s liberation",
    "American History":         r"pilgrim|mayflower|manifest destiny|lewis.*clark|gold rush|transcontinental railroad|industrial revolution.*america|prohibition.*america|suffragette.*america",
    "Ancient History":          r"roman empire|greek empire|ancient egypt|ancient china|mesopotamia|fertile crescent|julius caesar|cleopatra|alexander the great|trojan war|colosseum|parthenon|pyramids",
    "Medieval History":         r"feudal|crusade|black death|magna carta|charlemagne|genghis khan|marco polo|joan of arc|hundred years|knight.*medieval|castle.*medieval",
    "European History":         r"french revolution|napoleon|marie antoinette|waterloo|bismarck|otto.*germany|hapsburg|renaissance.*europe|protestant reformation|martin luther.*church",
    "World War I":              r"world war.*one|world war i|archduke franz|western front|trench|gallipoli|armistice|treaty of versailles|woodrow wilson.*war",
    "World War II":             r"world war.*two|world war ii|nazi|hitler|stalin|churchill|holocaust|auschwitz|d.day|pearl harbor|hiroshima|normandy|battle of britain",
    "Cold War":                 r"soviet union|ussr|iron curtain|berlin wall|cuban missile crisis|nuclear.*standoff|arms race|mccarthyism|sputnik|space race.*soviet",
    "World History":            r"colonialism|imperialism|independence movement|french revolution|industrial revolution|enlightenment|reformation|silk road",
    "World Capitals":           r"capital (city|of)|seat of government",
    "U.S. States & Cities":     r"\b(alabama|alaska|arizona|arkansas|california|colorado|connecticut|delaware|florida|georgia|hawaii|idaho|illinois|indiana|iowa|kansas|kentucky|louisiana|maine|maryland|massachusetts|michigan|minnesota|mississippi|missouri|montana|nebraska|nevada|new hampshire|new jersey|new mexico|new york|north carolina|north dakota|ohio|oklahoma|oregon|pennsylvania|rhode island|south carolina|south dakota|tennessee|texas|utah|vermont|virginia|washington|west virginia|wisconsin|wyoming)\b",
    "World Geography":          r"\bcapital\b|mountain range|river delta|archipelago|strait|peninsula|equator|hemisphere",
    "Astronomy & Space":        r"planet|star|galaxy|comet|asteroid|orbit|nasa|telescope|solar system|nebula|black hole|constellation|astronaut|spacecraft|supernova",
    "Biology":                  r"dna|rna|evolution|species|gene|chromosome|cell.*biology|ecosystem|photosynthesis|mitosis|meiosis|protein|enzyme",
    "Chemistry":                r"periodic table|chemical element|molecule|compound|atom|chemical bond|acid.*base|polymer|oxidation|reduction|isotope",
    "Physics":                  r"force|gravity|quantum|relativity|thermodynamic|electromagnetism|wave.*particle|velocity|momentum|newton.*law|einstein.*theory",
    "Earth Science":            r"volcano|earthquake|tectonic plate|mineral|rock.*geolog|fossil|erosion|atmosphere.*earth|ocean current|meteorolog",
    "Human Body & Medicine":    r"organ|muscle|bone|nerve|brain|heart|lung|liver|kidney|blood|surgery|diagnosis|symptom|vaccine|antibiotic|cancer|diabetes",
    "Science & Nature":         r"scientific|experiment|hypothesis|natural world|wildlife|habitat|predator|prey|food chain|climate change|biodiversity",
    "Mathematics":              r"\bequation\b|\btheorem\b|prime number|pythagorean|fibonacci|calculus|integer|polynomial|derivative|integral",
    "Shakespeare":              r"shakespeare|hamlet|macbeth|othello|falstaff|iago|prospero|oberon|titania|polonius|cordelia|desdemona|shylock|puck",
    "American Literature":      r"\b(twain|hemingway|fitzgerald|steinbeck|faulkner|whitman|dickinson|thoreau|emerson|hawthorne|melville|poe|morrison|updike|roth|carver|vonnegut|salinger|kerouac)\b",
    "British Literature":       r"\b(dickens|austen|bronte|hardy|orwell|woolf|kipling|chaucer|milton|keats|shelley|byron|tennyson|browning|eliot|swift|defoe|fielding|thackeray|forster|lawrence|greene|amis)\b",
    "Classic Literature":       r"\b(homer|dante|cervantes|tolstoy|dostoevsky|kafka|proust|joyce|chekhov|turgenev|flaubert|balzac|hugo|zola|ibsen|strindberg)\b",
    "Poetry":                   r"\bsonnet\b|\bode\b|\bpoem\b|\bpoet\b|\bverse\b|epic poem|haiku|laureate|iambic pentameter",
    "Children's Literature":    r"fairy tale|nursery rhyme|dr\.? seuss|roald dahl|beatrix potter|brothers grimm|hans christian andersen|grimm.*tale",
    "Literature":               r"\bnovel\b|\bfiction\b|\bnarrator\b|\bplot\b|\bchapter\b|\bcharacter.*book\b|literary|protagonist|antagonist",
    "Classical Music":          r"\b(beethoven|mozart|bach|chopin|brahms|handel|vivaldi|schubert|liszt|haydn|tchaikovsky|debussy|ravel|mahler|strauss|verdi|puccini|wagner)\b",
    "Jazz & Blues":             r"\b(armstrong|miles davis|coltrane|ellington|billie holiday|charlie parker|dizzy gillespie|thelonious monk|muddy waters|bb king|robert johnson)\b",
    "Rock & Pop Music":         r"\b(beatles|rolling stones|led zeppelin|pink floyd|bowie|elvis|jimi hendrix|queen.*band|nirvana|radiohead|michael jackson|madonna|prince.*musician|u2|fleetwood mac)\b",
    "Music":                    r"\bsong\b|\balbum\b|\bband\b|\bsinger\b|\blyric\b|\bmelody\b|\bchord\b|\brhythm\b|\bconcert\b|\btour\b.*music",
    "Painting & Sculpture":     r"\b(van gogh|picasso|monet|rembrandt|da vinci|michelangelo|rodin|warhol|dali|renoir|matisse|cézanne|gauguin|degas|klimt|kandinsky|pollock|basquiat)\b",
    "Architecture":             r"\b(frank lloyd wright|le corbusier|zaha hadid|mies van der rohe|gaudi|renzo piano)\b|skyscraper|cathedral|colosseum|parthenon|taj mahal",
    "Art & Architecture":       r"\bpainting\b|\bsculpture\b|\bcanvas\b|\bmural\b|\bfresco\b|\bbaroque\b|\bimpressionism\b|\bcubism\b|\babstract art\b|louvre|moma",
    "Theater & Dance":          r"broadway|musical theater|ballet|choreograph|tony award|west end|opera.*stage|mime|modern dance",
    "Oscar-Winning Films":      r"academy award|best picture|best director|best actor|best actress",
    "Film & TV":                r"\bfilm\b|\bmovie\b|\bdirector\b|\bactor\b|\bactress\b|\boscars?\b|\bcinema\b|\bscreenplay\b|\btelevision\b|\bsitcom\b|\bdrama.*series\b",
    "American Football":        r"\bnfl\b|super bowl|quarterback|touchdown|gridiron|\b(patriots|cowboys|packers|steelers|49ers|chiefs|bears|giants|eagles)\b",
    "Baseball":                 r"\bmlb\b|world series|pitcher|batting average|home run|\b(yankees|red sox|dodgers|cubs|giants|cardinals|braves)\b",
    "Basketball":               r"\bnba\b|slam dunk|three.pointer|\b(lakers|celtics|bulls|spurs|warriors|heat|cavaliers)\b|lebron james|michael jordan",
    "Soccer / Football":        r"\bfifa\b|premier league|la liga|bundesliga|champions league|world cup.*soccer|goal.*soccer|penalty kick",
    "Tennis":                   r"wimbledon|us open.*tennis|french open|australian open|grand slam|serena williams|roger federer|rafael nadal|novak djokovic",
    "Olympics":                 r"olympic games|gold medal|silver medal|bronze medal|olympic record|olympic champion",
    "Sports":                   r"\btournament\b|\bleague\b|\bplayoff\b|\bchampionship\b|\bathlete\b|\bcoach\b|\bstadium\b|\btrophy\b|hall of fame",
    "Wine & Spirits":           r"\bwine\b|\bchampagne\b|\bwhiskey\b|\bwhisky\b|\bbourbon\b|\bvodka\b|\bgin\b|\brum\b|\bbrandy\b|\btequila\b|\bwinery\b|\bvineyard\b",
    "Food & Drink":             r"\brecipe\b|\bingredient\b|\bcuisine\b|\bflavor\b|\bbaked\b|\bgrilled\b|\bcocktail\b|\bbeer\b|\bchef\b|\brestaurant\b|\bdish\b",
    "Foreign Languages":        r"french word|spanish word|german word|italian word|latin phrase|japanese word|translate|in (french|spanish|german|italian|latin|japanese)",
    "Word Origins & Etymology":  r"etymology|word origin|root word|latin root|greek root|borrowed word",
    "Wordplay & Puzzles":       r"anagram|palindrome|rhyme|homophone|portmanteau|acronym|wordplay|crossword",
    "Language & Words":         r"\bgrammar\b|\bvocabulary\b|\bprefix\b|\bsuffix\b|\bsynonym\b|\bantonym\b|\bverb\b|\bnoun\b|\badjective\b|\bspelling\b",
    "U.S. Government & Politics":r"congress|senate|supreme court|electoral college|filibuster|amendment.*constitution|bill of rights|political party.*us",
    "World Politics":           r"united nations|nato|european union|diplomacy|treaty|prime minister|chancellor|parliament|geopolitic",
    "Economics":                r"gdp|inflation|recession|stock market|supply.*demand|free trade|tariff|keynesian|capitalism|socialism",
    "Psychology":               r"freud|jung|pavlov|skinner|cognitive.*psycholog|therapy|mental health|personality disorder|neuroscience",
    "The Bible & Christianity":  r"\bbible\b|\bbiblical\b|\btestament\b|\bgospel\b|\bjesus\b|\bchrist\b|\bapostle\b|\bpsalm\b|\bproverb\b|\bgenesis\b|\bexodus\b",
    "World Religions":          r"\bislam\b|\bmuslim\b|\bquran\b|\bhindu\b|\bbuddhis\b|\bjudaism\b|\bsikhism\b|\btaoism\b|\bmosque\b|\bsynagogue\b",
    "Philosophy":               r"\b(plato|aristotle|socrates|kant|descartes|nietzsche|hegel|locke|hume|sartre|camus|wittgenstein|rousseau)\b|existential|utilitari|epistemolog",
    "Greek & Roman Mythology":  r"\b(zeus|hera|apollo|athena|poseidon|ares|aphrodite|hermes|hercules|odysseus|achilles|perseus|medusa|minotaur|jupiter|juno|mars|venus|mercury|neptune|vulcan|diana|minerva)\b",
    "Norse Mythology":          r"\b(thor|odin|loki|freya|valhalla|asgard|ragnarok|yggdrasil|frigg|tyr|baldur)\b",
    "Mythology":                r"\bmyth\b|\bmythology\b|\blegend\b|\bfolklore\b|\bfable\b|\bdemigod\b|\bdeity\b|\bpantheon\b",
    "Computers & Technology":   r"computer|software|hardware|internet|coding|programming|algorithm|artificial intelligence|\bai\b|machine learning|silicon valley|\bapp\b|\boperating system\b",
    "Inventions & Inventors":   r"invention|inventor|patent|\b(edison|tesla|bell|wright brothers|gutenberg|galileo|newton|darwin|curie|pasteur)\b",
    "Animals & Wildlife":       r"\b(lion|tiger|elephant|giraffe|whale|dolphin|eagle|shark|crocodile|gorilla|chimpanzee|penguin|polar bear|wolf|fox|deer|bear|rabbit|squirrel)\b",
    "Royalty & Nobility":       r"\b(king|queen|prince|princess|monarch|emperor|empress|tsar|sultan|pharaoh)\b.*\b(of|the)\b|royal family|buckingham|versailles",
    "Crime & Law":              r"\b(murder|theft|fraud|robbery|trial|verdict|jury|detective|prosecutor|defendant|felony|misdemeanor|forensic)\b",
    "Holidays & Traditions":    r"\b(christmas|thanksgiving|halloween|easter|hanukkah|diwali|ramadan|passover|new year)\b",
}

ALL_TAGS = list(dict.fromkeys(list(CATEGORY_MAP.keys()) + list(CONTENT_MAP.keys()) + ["Other"]))

def identify_universal_cat(row):
    category = str(row.get('category', '')).lower()
    clue_text = str(row.get('answer', '')).lower()
    combined = f"{category} {clue_text}"

    # Pass 1: category string only
    for label, pattern in CATEGORY_MAP.items():
        if re.search(pattern, category):
            return label

    # Pass 2: combined category + clue content
    for label, pattern in CONTENT_MAP.items():
        if re.search(pattern, combined):
            return label

    return "Other"

# --- 1b. CLUE TAG PERSISTENCE (Supabase) ---
# Manual tag overrides are saved per-clue so the correct tag is always shown.
# Batch-fetched at session start; zero latency during play.

@st.cache_resource
def _get_supabase():
    """Cached Supabase client — created once per server lifetime."""
    try:
        from supabase import create_client
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except Exception as e:
        st.warning(f"⚠️ Supabase unavailable: {e}")
        return None

def _clue_id(row) -> str:
    """Stable fingerprint for a clue: sha256 of category+answer+question."""
    raw = f"{row.get('category','')}{row.get('answer','')}{row.get('question','')}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]

def _fetch_tag_overrides(clue_ids: list[str]) -> dict:
    """
    Batch-fetch saved tags for a list of clue_ids from Supabase.
    Returns {clue_id: tag_string}. Empty dict on failure.
    """
    if not clue_ids:
        return {}
    try:
        client = _get_supabase()
        if client is None:
            return {}
        result = (
            client.table("clue_tags")
            .select("clue_id, tag")
            .in_("clue_id", clue_ids)
            .execute()
        )
        return {row["clue_id"]: row["tag"] for row in (result.data or [])}
    except Exception:
        return {}

def _save_tag_override(clue_id: str, tag: str):
    """Upsert a single manual tag override to Supabase."""
    try:
        client = _get_supabase()
        if client is None:
            return
        client.table("clue_tags").upsert({
            "clue_id": clue_id,
            "tag":     tag,
        }).execute()
    except Exception as e:
        st.warning(f"⚠️ Could not save tag: {e}")

# --- 1c. GAME STATS PERSISTENCE (Supabase) ---
# Weakness tracker stats and winnings are stored in the drill_progress table
# (same row as SRS data) under the game_stats and winnings columns.
# Loaded once per browser session; written after every answered clue.

def _load_game_stats() -> tuple[dict, int]:
    """
    Returns (stats_dict, winnings_int).
    stats_dict: {category: {"correct": int, "total": int}}
    Falls back to empty stats on any failure.
    """
    empty_stats = {cat: {"correct": 0, "total": 0} for cat in ALL_TAGS}
    try:
        client = _get_supabase()
        if client is None:
            return empty_stats, 0
        result = (
            client.table("drill_progress")
            .select("game_stats, winnings")
            .eq("user_id", "default")
            .single()
            .execute()
        )
        row = result.data
        if not row:
            return empty_stats, 0
        saved = row.get("game_stats") or {}
        winnings = int(row.get("winnings") or 0)
        # Merge saved stats into full tag list (handles new tags added later)
        stats = empty_stats.copy()
        for cat, data in saved.items():
            if cat in stats:
                stats[cat] = data
        return stats, winnings
    except Exception:
        return empty_stats, 0

def _save_game_stats(stats: dict, winnings: int):
    """Upsert game stats and winnings back to Supabase."""
    try:
        client = _get_supabase()
        if client is None:
            return
        client.table("drill_progress").upsert({
            "user_id":    "default",
            "game_stats": stats,
            "winnings":   winnings,
        }).execute()
    except Exception as e:
        st.warning(f"⚠️ Could not save stats: {e}")

def _prime_tag_cache(pool_df):
    """
    Called once after data loads. Batch-fetches saved tags for all clues
    in the current filtered pool and stores them in session_state.
    Subsequent lookups are pure dict reads — no DB calls during play.
    """
    if pool_df is None or "tag_cache" in st.session_state:
        return
    clue_ids = [_clue_id(pool_df.iloc[i]) for i in range(len(pool_df))]
    st.session_state.tag_cache = _fetch_tag_overrides(clue_ids)
    # Also store a mapping from clue_id → df index for quick reverse lookup
    st.session_state.clue_id_map = {
        _clue_id(pool_df.iloc[i]): i for i in range(len(pool_df))
    }

def get_tag_for_clue(row) -> str:
    """
    Return the tag for a clue: DB override if saved, otherwise run engine.
    """
    cid = _clue_id(row)
    cache = st.session_state.get("tag_cache", {})
    if cid in cache:
        return cache[cid]
    return identify_universal_cat(row)


# Presidents whose last name alone is ambiguous (multiple presidents share it)
SHARED_SURNAMES = {"adams", "harrison", "johnson", "roosevelt", "bush"}

# Known aliases → canonical form used for matching
PRESIDENT_ALIASES = {
    "jfk":             "john kennedy",
    "fdr":             "franklin roosevelt",
    "lbj":             "lyndon johnson",
    "teddy":           "theodore roosevelt",
    "teddy roosevelt": "theodore roosevelt",
    "ike":             "eisenhower",
}

def normalize(text):
    """Strip articles, punctuation, extra whitespace, lowercase."""
    text = str(text).lower().strip()
    text = re.sub(r'\b(a|an|the)\b', '', text)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def fuzzy_match(user_ans, correct_ans, threshold=75):
    """
    Returns (is_correct: bool, score: int).
    - Accepts a single last name as correct UNLESS it's on the shared-surname
      list (Adams, Harrison, Johnson, Roosevelt, Tyler, Bush) — those require
      a first name.
    - Accepts aliases: JFK, FDR, LBJ, Teddy (Roosevelt), Ike (Eisenhower).
    - Otherwise uses character-level fuzzy similarity.
    """
    import difflib
    u_raw  = normalize(user_ans)
    c_norm = normalize(correct_ans)

    if not u_raw:
        return False, 0

    # Reject bare shared surname (e.g. "Roosevelt" or "Bush" with no first name)
    parts = u_raw.split()
    if len(parts) == 1 and parts[0] in SHARED_SURNAMES:
        return False, 0

    # Expand known aliases (jfk → john kennedy, etc.)
    u = PRESIDENT_ALIASES.get(u_raw, u_raw)

    # Exact / substring match — also try stripping middle initials from correct answer
    c_no_initials = re.sub(r'\b[a-z]\b', '', c_norm).strip()
    c_no_initials = re.sub(r'\s+', ' ', c_no_initials).strip()
    for c_variant in [c_norm, c_no_initials]:
        if u == c_variant or u in c_variant or c_variant in u:
            return True, 100

    # Last-name match: if the user typed a single word, check if it matches
    # any word in the correct answer (handles "Ford" matching "Gerald Ford")
    u_parts = u.split()
    c_parts = c_norm.split()
    if len(u_parts) == 1 and u_parts[0] in c_parts:
        return True, 100

    # Full fuzzy similarity
    ratio = difflib.SequenceMatcher(None, u, c_norm).ratio() * 100
    score = int(ratio)
    return score >= threshold, min(score, 100)

# --- 3. CUSTOM CSS ---
st.markdown("""
    <style>
    .category-box {
        background-color: #060ce9;
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 25px;
    }
    .category-text {
        font-family: 'Arial Black', sans-serif;
        font-weight: bold;
        font-size: 28px;
        text-transform: uppercase;
    }
    div.stButton > button:first-child {
        background-color: #475569 !important;
        color: white !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. DATA LOADING (SEASON CAPTURE) ---
@st.cache_data
def load_all_seasons():
    files = glob.glob("*.tsv")
    if not files:
        return None
    
    all_chunks = []
    for f in files:
        try:
            temp_df = pd.read_csv(f, sep='\t', low_memory=False)
            s_match = re.search(r'\d+', f)
            temp_df['season'] = s_match.group() if s_match else "??"
            all_chunks.append(temp_df)
        except:
            continue
            
    if not all_chunks:
        return None
    
    df = pd.concat(all_chunks, ignore_index=True)
    return df.dropna(subset=['answer', 'question']).sample(frac=1).reset_index(drop=True)

df = load_all_seasons()
_prime_tag_cache(df)

# --- 5. STATE MANAGEMENT ---
if 'stats' not in st.session_state:
    # Load persisted stats from Supabase on first load
    _db_stats, _db_winnings = _load_game_stats()
    st.session_state.stats    = _db_stats
    st.session_state.winnings = _db_winnings
elif set(ALL_TAGS) - set(st.session_state.stats.keys()):
    for tag in ALL_TAGS:
        if tag not in st.session_state.stats:
            st.session_state.stats[tag] = {"correct": 0, "total": 0}

if 'winnings' not in st.session_state:
    st.session_state.winnings = 0

if 'settings' not in st.session_state:
    st.session_state.settings = {
        "close_enough": False,
        "close_enough_threshold": 75,
        "difficulty": "All",          # "All", "Easy ($200-$600)", "Medium ($800-$1200)", "Hard ($1600+)"
    }

if 'settings' not in st.session_state:
    st.session_state.settings = {
        "close_enough": False,
        "close_enough_threshold": 75,
        "difficulty": "All",
        "timer_enabled": True,
        "timer_seconds": 15,
        "session_length": 0,       # 0 = unlimited
    }
else:
    # forward-compat: add new keys if missing
    for k, v in [("timer_enabled", True), ("timer_seconds", 15), ("session_length", 0)]:
        if k not in st.session_state.settings:
            st.session_state.settings[k] = v

for k, v in [("clue_history", []), ("history_pos", -1)]:
    if k not in st.session_state:
        st.session_state[k] = v

if 'idx' not in st.session_state:
    st.session_state.idx = 0
    st.session_state.show = False
    st.session_state.current_tag = "Other"
    st.session_state.initialized = False
    st.session_state.user_answer = ""
    st.session_state.match_result = None
    st.session_state.question_num = 0
    st.session_state.session_active = True
    st.session_state.clue_start_time = None
    st.session_state.timed_out = False
    # History for back/forward navigation (last 25 answered clues)
    # Each entry: {"idx": df_idx, "tag": str, "correct": bool, "clue_value": int,
    #              "user_answer": str, "match_result": tuple|None, "show": bool}
    st.session_state.clue_history = []
    st.session_state.history_pos  = -1   # -1 = live (at the frontier)

DIFFICULTY_RANGES = {
    "All":                  (0, 999999),
    "Easy ($200–$600)":     (200, 600),
    "Medium ($800–$1200)":  (800, 1200),
    "Hard ($1600+)":        (1600, 999999),
    "Final Jeopardy":       None,          # special: filter by round == 3
}

def get_filtered_pool():
    if df is None:
        return None
    diff = st.session_state.settings["difficulty"]
    if diff == "Final Jeopardy":
        pool = df[df.get('round', pd.Series(dtype=int)) == 3] if 'round' in df.columns else df[df['clue_value'].apply(lambda v: int(v or 0) == 0)]
    else:
        lo, hi = DIFFICULTY_RANGES[diff]
        pool = df[df['clue_value'].apply(lambda v: lo <= int(v or 0) <= hi)]
    return pool if len(pool) > 0 else df

import time

def get_next():
    pool = get_filtered_pool()
    if pool is not None:
        st.session_state.idx = pool.sample(1).index[0]
        st.session_state.show = False
        st.session_state.user_answer = ""
        st.session_state.match_result = None
        st.session_state.timed_out = False
        st.session_state.clue_start_time = time.time()
        row = df.iloc[st.session_state.idx]
        st.session_state.current_tag = get_tag_for_clue(row)
        st.session_state.history_pos = -1   # back at frontier
        st.session_state.initialized = True

def _push_history(df_idx, tag, correct, clue_value, user_answer, match_result):
    """Push a completed clue onto the history stack (max 25)."""
    entry = {
        "df_idx":       df_idx,
        "tag":          tag,
        "correct":      correct,
        "clue_value":   clue_value,
        "user_answer":  user_answer,
        "match_result": match_result,
    }
    hist = st.session_state.clue_history
    hist.append(entry)
    if len(hist) > 25:
        hist.pop(0)
    st.session_state.clue_history = hist

def _recalculate_from_history():
    """Recompute stats and winnings from scratch using the full history."""
    stats = {cat: {"correct": 0, "total": 0} for cat in ALL_TAGS}
    winnings = 0
    for entry in st.session_state.clue_history:
        cat = entry["tag"]
        if cat not in stats:
            stats[cat] = {"correct": 0, "total": 0}
        stats[cat]["total"] += 1
        if entry["correct"]:
            stats[cat]["correct"] += 1
            winnings += entry["clue_value"]
        else:
            winnings -= entry["clue_value"]
    return stats, winnings

def record_and_advance(correct: bool, clue_value: int, u_cat: str):
    """Score current clue, push to history, then get next clue."""
    _push_history(
        df_idx      = st.session_state.idx,
        tag         = u_cat,
        correct     = correct,
        clue_value  = clue_value,
        user_answer = st.session_state.get("user_answer", ""),
        match_result= st.session_state.match_result,
    )
    if correct:
        st.session_state.stats[u_cat]["correct"] += 1
        st.session_state.winnings += clue_value
    else:
        st.session_state.winnings -= clue_value
    st.session_state.stats[u_cat]["total"] += 1
    _save_game_stats(st.session_state.stats, st.session_state.winnings)
    st.session_state.question_num += 1
    limit = st.session_state.settings["session_length"]
    if limit > 0 and st.session_state.question_num >= limit:
        st.session_state.session_active = False
    else:
        get_next()

# --- 6. MAIN UI ---
tab_game, tab_drill = st.tabs(["🎯 Jeopardy Trainer", "🧠 Drill Mode"])

with tab_game:
    if df is None:
        st.error("No .tsv files found in the folder!")

    elif not st.session_state.get('session_active', True):
        # ── SESSION COMPLETE SCREEN ────────────────────────────────────────
        total_q   = st.session_state.question_num
        total_cor = sum(d["correct"] for d in st.session_state.stats.values())
        pct       = int(total_cor / total_q * 100) if total_q else 0
        win       = st.session_state.winnings

        st.markdown("## 🏆 Session Complete!")
        st.markdown(f"**Questions answered:** {total_q}")
        st.markdown(f"**Correct:** {total_cor} ({pct}%)")
        st.markdown(f"**Winnings:** {'$' if win >= 0 else '-$'}{abs(win):,}")

        st.markdown("---")
        st.markdown("### Category Breakdown")
        for cat, data in st.session_state.stats.items():
            if data["total"] > 0:
                acc = data["correct"] / data["total"] * 100
                st.markdown(f"**{cat}** — {acc:.0f}% ({data['correct']}/{data['total']})")

        st.markdown("---")
        if st.button("▶️ Start New Session", type="primary", use_container_width=True):
            st.session_state.session_active = True
            st.session_state.question_num = 0
            get_next()
            st.rerun()
        if st.button("🔄 Reset All Stats & Start Over", use_container_width=True):
            st.session_state.stats    = {cat: {"correct": 0, "total": 0} for cat in ALL_TAGS}
            st.session_state.winnings = 0
            _save_game_stats(st.session_state.stats, 0)
            st.session_state.session_active = True
            st.session_state.question_num = 0
            get_next()
            st.rerun()

    else:
        if not st.session_state.initialized:
            get_next()

        # ── Determine if we're viewing a history entry or the live clue ──────
        hist     = st.session_state.clue_history
        hist_pos = st.session_state.history_pos   # -1 = live frontier
        at_frontier = (hist_pos == -1)

        if at_frontier:
            clue      = df.iloc[st.session_state.idx]
            u_cat     = st.session_state.current_tag
        else:
            entry     = hist[hist_pos]
            clue      = df.iloc[entry["df_idx"]]
            u_cat     = entry["tag"]

        _raw_value         = int(clue.get('clue_value') or 0)
        clue_value         = _raw_value if _raw_value > 0 else 0
        clue_value_display = "Final Jeopardy" if _raw_value == 0 else f"${_raw_value}"
        close_enough_on    = st.session_state.settings["close_enough"]
        correct_response   = str(clue['question'])
        timer_on           = close_enough_on and st.session_state.settings["timer_enabled"] and at_frontier
        timer_limit        = st.session_state.settings["timer_seconds"]
        session_limit      = st.session_state.settings["session_length"]

        # ── BACK / FORWARD NAV BAR ────────────────────────────────────────────
        can_go_back    = len(hist) > 0 and hist_pos != 0
        can_go_forward = hist_pos != -1

        nav_c1, nav_c2, nav_c3 = st.columns([1, 3, 1])
        with nav_c1:
            if st.button("← Back", disabled=not can_go_back,
                         use_container_width=True, key="trainer_back"):
                if hist_pos == -1:
                    st.session_state.history_pos = len(hist) - 1
                else:
                    st.session_state.history_pos = hist_pos - 1
                st.rerun()
        with nav_c2:
            if not at_frontier:
                st.markdown(
                    f"<div style='text-align:center;color:#9090B0;padding-top:6px;"
                    f"font-size:13px;font-weight:600;'>"
                    f"Reviewing clue {hist_pos + 1} of {len(hist)} — "
                    f"<span style='color:#F0B429'>history</span></div>",
                    unsafe_allow_html=True,
                )
            else:
                pos_label = f"Q {st.session_state.question_num + 1}"
                if session_limit > 0:
                    pos_label += f" of {session_limit}"
                st.markdown(
                    f"<div style='text-align:center;color:#9090B0;padding-top:6px;"
                    f"font-size:13px;font-weight:600;'>{pos_label}</div>",
                    unsafe_allow_html=True,
                )
        with nav_c3:
            if st.button("Forward →", disabled=not can_go_forward,
                         use_container_width=True, key="trainer_fwd"):
                if hist_pos == len(hist) - 1:
                    st.session_state.history_pos = -1
                else:
                    st.session_state.history_pos = hist_pos + 1
                st.rerun()

        # ── QUESTION COUNTER & TIMER BAR ──────────────────────────────────────
        elapsed   = 0
        time_left = timer_limit
        timed_out = st.session_state.get('timed_out', False) if at_frontier else entry.get("timed_out", False)

        if timer_on and st.session_state.clue_start_time and not st.session_state.show:
            elapsed   = time.time() - st.session_state.clue_start_time
            time_left = max(0, timer_limit - elapsed)
            timed_out = st.session_state.get('timed_out', False)

        if timer_on and not (st.session_state.show if at_frontier else True):
            elapsed_display = min(elapsed, timer_limit)
            remaining = max(0, timer_limit - elapsed_display)
            color = "#22c55e" if remaining > timer_limit * 0.4 else ("#f59e0b" if remaining > timer_limit * 0.2 else "#ef4444")
            st.markdown(
                f'<div style="text-align:right;font-size:1.4rem;font-weight:bold;color:{color}">⏱ {remaining:.0f}s</div>',
                unsafe_allow_html=True
            )

        if timer_on and not st.session_state.show and not timed_out:
            st.progress(max(0.0, time_left / timer_limit))

        # ── CLUE DISPLAY ──────────────────────────────────────────────────────
        st.markdown(f'<div class="category-box"><div class="category-text">{clue["category"]}</div></div>', unsafe_allow_html=True)
        st.markdown(f"### {clue['answer']}")
        st.caption(f"Season {clue['season']} | {clue_value_display}")

        # ── TAG SELECTOR ──────────────────────────────────────────────────────
        sorted_tags  = sorted([t for t in ALL_TAGS if t != "Other"]) + ["Other"]
        selected_tag = st.selectbox(
            "Study Tag",
            options=sorted_tags,
            index=sorted_tags.index(u_cat) if u_cat in sorted_tags else 0,
            key=f"retag_select_{st.session_state.idx}_{hist_pos}",
            label_visibility="collapsed"
        )
        tag_changed = selected_tag != u_cat
        if tag_changed:
            cid = _clue_id(clue)
            _save_tag_override(cid, selected_tag)
            if "tag_cache" in st.session_state:
                st.session_state.tag_cache[cid] = selected_tag
            if at_frontier:
                st.session_state.current_tag = selected_tag
            else:
                hist[hist_pos]["tag"] = selected_tag
                st.session_state.clue_history = hist
            u_cat = selected_tag
            st.rerun()

        # ── HISTORY MODE: show result + allow re-rating ───────────────────────
        if not at_frontier:
            prev_correct = entry["correct"]
            st.info(f"{'✅ You got this correct' if prev_correct else '❌ You missed this'} — clue value: {clue_value_display}")
            st.success(f"RESPONSE: {correct_response.upper()}")
            if entry.get("user_answer"):
                st.caption(f"Your answer was: *\"{entry['user_answer']}\"*")

            st.markdown("**Change your rating:**")
            rc1, rc2, rc3 = st.columns(3)
            with rc1:
                if st.button("✅ Mark Correct", use_container_width=True, key="hist_correct"):
                    if not prev_correct:
                        hist[hist_pos]["correct"] = True
                        st.session_state.clue_history = hist
                        new_stats, new_winnings = _recalculate_from_history()
                        st.session_state.stats    = new_stats
                        st.session_state.winnings = new_winnings
                        _save_game_stats(new_stats, new_winnings)
                    st.rerun()
            with rc2:
                if st.button("❌ Mark Wrong", use_container_width=True, key="hist_wrong"):
                    if prev_correct:
                        hist[hist_pos]["correct"] = False
                        st.session_state.clue_history = hist
                        new_stats, new_winnings = _recalculate_from_history()
                        st.session_state.stats    = new_stats
                        st.session_state.winnings = new_winnings
                        _save_game_stats(new_stats, new_winnings)
                    st.rerun()
            with rc3:
                if st.button("▶ Back to Current", use_container_width=True,
                             type="primary", key="hist_resume"):
                    st.session_state.history_pos = -1
                    st.rerun()

        # ── LIVE MODE: normal answer/rating flow ──────────────────────────────
        elif close_enough_on:
            if not st.session_state.show:
                user_ans = st.text_input(
                    "Your answer:",
                    value=st.session_state.get("user_answer", ""),
                    placeholder="Type your response and press Enter or Check Answer...",
                    key=f"ans_input_{st.session_state.idx}",
                )
                if st.button("CHECK ANSWER", use_container_width=True, type="primary"):
                    elapsed_now = time.time() - st.session_state.clue_start_time if st.session_state.clue_start_time else 0
                    if timer_on and elapsed_now > timer_limit:
                        st.session_state.timed_out    = True
                        st.session_state.user_answer  = user_ans or "⏰ Time's up!"
                        st.session_state.match_result = (False, 0)
                    else:
                        is_correct, score = fuzzy_match(
                            user_ans, correct_response,
                            threshold=st.session_state.settings["close_enough_threshold"]
                        )
                        st.session_state.user_answer  = user_ans
                        st.session_state.match_result = (is_correct, score)
                    st.session_state.show = True
                    st.rerun()
            else:
                result     = st.session_state.match_result
                is_correct, score = result if result else (None, 0)

                st.success(f"RESPONSE: {correct_response.upper()}")

                if timed_out:
                    st.error(f"⏰ Time's up! ({timer_limit}s limit)")
                elif is_correct:
                    st.success(f"✅ Match! Similarity: {score}%  |  You wrote: *\"{st.session_state.user_answer}\"*")
                else:
                    st.error(f"❌ No match. Similarity: {score}%  |  You wrote: *\"{st.session_state.user_answer}\"*")

                next_label = "➡️ NEXT (Correct)" if is_correct else "➡️ NEXT (Wrong)"
                if st.button(next_label, use_container_width=True, type="primary"):
                    record_and_advance(bool(is_correct), clue_value, u_cat)
                    st.rerun()

                st.caption("Override auto-grade:")
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("✅ Mark Correct", use_container_width=True):
                        record_and_advance(True, clue_value, u_cat)
                        st.rerun()
                with c2:
                    if st.button("❌ Mark Wrong", use_container_width=True):
                        record_and_advance(False, clue_value, u_cat)
                        st.rerun()
                with c3:
                    if st.button("⏭️ Skip", use_container_width=True):
                        st.session_state.question_num += 1
                        limit = st.session_state.settings["session_length"]
                        if limit > 0 and st.session_state.question_num >= limit:
                            st.session_state.session_active = False
                        else:
                            get_next()
                        st.rerun()

        else:
            # Classic self-report mode
            if not st.session_state.show:
                if st.button("REVEAL RESPONSE", use_container_width=True, type="primary"):
                    st.session_state.show = True
                    st.rerun()
            else:
                st.success(f"RESPONSE: {correct_response.upper()}")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ I GOT IT", use_container_width=True):
                        record_and_advance(True, clue_value, u_cat)
                        st.rerun()
                with c2:
                    if st.button("❌ I MISSED IT", use_container_width=True):
                        record_and_advance(False, clue_value, u_cat)
                        st.rerun()

# --- 7. SIDEBAR ---
st.sidebar.title("📊 Training Progress")

total_correct = sum(d["correct"] for d in st.session_state.stats.values())
total_seen = sum(d["total"] for d in st.session_state.stats.values())

col_a, col_b = st.sidebar.columns(2)
col_a.metric("Total Correct", f"{total_correct} / {total_seen}")
winnings = st.session_state.get('winnings', 0)
col_b.metric("Winnings", f"{'$' if winnings >= 0 else '-$'}{abs(winnings):,}")

# ── SETTINGS ──────────────────────────────────────────────────────────────
st.sidebar.divider()
st.sidebar.subheader("⚙️ Settings")

# Difficulty filter
diff_choice = st.sidebar.radio(
    "Difficulty Filter",
    options=list(DIFFICULTY_RANGES.keys()),
    index=list(DIFFICULTY_RANGES.keys()).index(st.session_state.settings["difficulty"]),
    horizontal=False,
)
if diff_choice != st.session_state.settings["difficulty"]:
    st.session_state.settings["difficulty"] = diff_choice
    get_next()
    st.rerun()

if st.session_state.settings["difficulty"] == "Final Jeopardy":
    st.sidebar.caption("🎯 These are single, high-stakes clues — one per episode. Great for simulating pressure situations.")

st.sidebar.divider()

# Close enough mode toggle
close_toggle = st.sidebar.toggle(
    "🧠 Close Enough Mode",
    value=st.session_state.settings["close_enough"],
    help="Type your answer and let the app grade it automatically using fuzzy matching."
)
if close_toggle != st.session_state.settings["close_enough"]:
    st.session_state.settings["close_enough"] = close_toggle
    st.session_state.show = False
    st.session_state.user_answer = ""
    st.session_state.match_result = None
    st.rerun()

if st.session_state.settings["close_enough"]:
    threshold = st.sidebar.slider(
        "Match Sensitivity",
        min_value=50, max_value=95,
        value=st.session_state.settings["close_enough_threshold"],
        step=5,
        help="Higher = stricter grading. 75 is recommended."
    )
    if threshold != st.session_state.settings["close_enough_threshold"]:
        st.session_state.settings["close_enough_threshold"] = threshold

    st.sidebar.markdown("**⏱ Timer**")
    timer_toggle = st.sidebar.toggle(
        "Enable Timer",
        value=st.session_state.settings["timer_enabled"],
        key="timer_toggle"
    )
    if timer_toggle != st.session_state.settings["timer_enabled"]:
        st.session_state.settings["timer_enabled"] = timer_toggle
        st.session_state.clue_start_time = time.time()
        st.session_state.timed_out = False

    if st.session_state.settings["timer_enabled"]:
        t_secs = st.sidebar.slider(
            "Seconds per clue",
            min_value=5, max_value=60,
            value=st.session_state.settings["timer_seconds"],
            step=5,
            help="15 seconds matches the real Jeopardy! online test."
        )
        if t_secs != st.session_state.settings["timer_seconds"]:
            st.session_state.settings["timer_seconds"] = t_secs
            st.session_state.clue_start_time = time.time()

    st.sidebar.markdown("**🔢 Session Length**")
    session_opts = {"Unlimited": 0, "10 Questions": 10, "25 Questions": 25, "50 Questions": 50}
    current_label = next((k for k, v in session_opts.items() if v == st.session_state.settings["session_length"]), "Unlimited")
    chosen_label = st.sidebar.selectbox(
        "Questions per session",
        options=list(session_opts.keys()),
        index=list(session_opts.keys()).index(current_label),
        help="50 questions matches the real Jeopardy! online test length."
    )
    new_session_len = session_opts[chosen_label]
    if new_session_len != st.session_state.settings["session_length"]:
        st.session_state.settings["session_length"] = new_session_len

# ── WEAKNESS TRACKER ──────────────────────────────────────────────────────
st.sidebar.divider()
st.sidebar.subheader("Weakness Tracker")
for cat, data in st.session_state.stats.items():
    if data["total"] > 0:
        acc = (data["correct"] / data["total"]) * 100
        st.sidebar.write(f"**{cat}**")
        st.sidebar.progress(acc / 100)
        st.sidebar.caption(f"{acc:.0f}% accuracy ({data['total']} clues)")

st.sidebar.divider()
if st.sidebar.button("🔄 REFRESH ALL STATS", use_container_width=True):
    st.session_state.stats    = {cat: {"correct": 0, "total": 0} for cat in ALL_TAGS}
    st.session_state.winnings = 0
    _save_game_stats(st.session_state.stats, 0)
    st.rerun()

with tab_drill:
    render_drill_mode()
