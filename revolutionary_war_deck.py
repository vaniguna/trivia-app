"""
revolutionary_war_deck.py — Comprehensive American Revolutionary War drill deck.

Answer matching notes (handled in drill_mode.py):
- "Adams" alone should be rejected — both John Adams and Samuel Adams are major figures
- All other surnames are unambiguous within this deck
"""

REVOLUTIONARY_WAR_DECK = {
    "name": "American Revolutionary War",
    "icon": "🦅",
    "description": "Key battles, figures, dates, documents, and events of the American Revolution",
    "cards": [

        # ── OVERVIEW & DATES ─────────────────────────────────────────────────
        {"q": "Years of the American Revolutionary War", "a": "1775–1783"},
        {"q": "Year the Declaration of Independence was signed", "a": "1776"},
        {"q": "Year the Revolutionary War officially ended", "a": "1783"},
        {"q": "Treaty that ended the Revolutionary War", "a": "Treaty of Paris"},
        {"q": "Year the Treaty of Paris was signed", "a": "1783"},
        {"q": "The first shots of the Revolutionary War were fired at these two towns", "a": "Lexington and Concord"},
        {"q": "Date of the first shots at Lexington and Concord", "a": "April 19, 1775"},
        {"q": "The colonial army was called this", "a": "Continental Army"},
        {"q": "Commander-in-chief of the Continental Army", "a": "George Washington"},

        # ── CAUSES & LEAD-UP ─────────────────────────────────────────────────
        {"q": "Rallying cry of the Revolution: 'No taxation without...'", "a": "Representation"},
        {"q": "1765 law that taxed legal documents, newspapers, and pamphlets in the colonies", "a": "Stamp Act"},
        {"q": "1767 laws that taxed imported goods like glass, paper, and tea", "a": "Townshend Acts"},
        {"q": "1773 protest in which colonists dumped British tea into Boston Harbor", "a": "Boston Tea Party"},
        {"q": "Laws passed by Britain in 1774 to punish Massachusetts, called this by colonists", "a": "Intolerable Acts (Coercive Acts)"},
        {"q": "March 1770 incident in which British soldiers killed five colonists in Boston", "a": "Boston Massacre"},
        {"q": "Colonists who supported independence from Britain", "a": "Patriots"},
        {"q": "Colonists who remained loyal to the British Crown", "a": "Loyalists (Tories)"},
        {"q": "Secret colonial organization that organized resistance to British rule", "a": "Sons of Liberty"},
        {"q": "Leader of the Sons of Liberty in Boston", "a": "Samuel Adams"},

        # ── KEY DOCUMENTS ────────────────────────────────────────────────────
        {"q": "Document declaring the colonies' independence, adopted July 4, 1776", "a": "Declaration of Independence"},
        {"q": "Primary author of the Declaration of Independence", "a": "Thomas Jefferson"},
        {"q": "Famous 1776 pamphlet by Thomas Paine that urged independence", "a": "Common Sense"},
        {"q": "Author of 'Common Sense'", "a": "Thomas Paine"},
        {"q": "Thomas Paine's series of essays written during the war, beginning 'These are the times that try men's souls'", "a": "The American Crisis"},
        {"q": "First constitution of the United States, ratified 1781", "a": "Articles of Confederation"},
        {"q": "The Declaration of Independence opens with these famous words", "a": "We hold these truths to be self-evident"},
        {"q": "This body adopted the Declaration of Independence", "a": "Second Continental Congress"},
        {"q": "City where the Continental Congress met", "a": "Philadelphia"},
        {"q": "President of the Continental Congress who signed the Declaration with the largest signature", "a": "John Hancock"},

        # ── MAJOR BATTLES ────────────────────────────────────────────────────
        {"q": "First major battle of the Revolution, fought near Boston in June 1775", "a": "Battle of Bunker Hill"},
        {"q": "Battle of Bunker Hill was actually fought mostly on this nearby hill", "a": "Breed's Hill"},
        {"q": "Turning point battle of the Revolution, October 1777, convinced France to ally with America", "a": "Battle of Saratoga"},
        {"q": "British general who surrendered at Saratoga", "a": "John Burgoyne"},
        {"q": "Final major battle of the Revolutionary War, 1781", "a": "Battle of Yorktown"},
        {"q": "British general who surrendered at Yorktown", "a": "Lord Cornwallis"},
        {"q": "Washington's famous crossing of the Delaware River led to victory at this battle", "a": "Battle of Trenton"},
        {"q": "Date of Washington's crossing of the Delaware", "a": "December 26, 1776 (Christmas night)"},
        {"q": "Battle in New Jersey following Trenton, a second American victory", "a": "Battle of Princeton"},
        {"q": "1777 battle in Pennsylvania where British forces defeated Washington", "a": "Battle of Brandywine"},
        {"q": "Washington's army endured a brutal winter here in 1777–1778", "a": "Valley Forge"},
        {"q": "1776 battle in which Washington was forced to retreat from New York City", "a": "Battle of Long Island (Battle of Brooklyn)"},
        {"q": "1781 naval battle that cut off Cornwallis's escape route before Yorktown", "a": "Battle of the Chesapeake (Battle of the Capes)"},
        {"q": "Southern campaign battle where the British crushed the Americans in 1780", "a": "Battle of Camden"},
        {"q": "American victory at Cowpens in 1781 was a turning point in this region", "a": "The South (Southern Campaign)"},

        # ── REVERSE: BATTLE → SIGNIFICANCE ──────────────────────────────────
        {"q": "Which battle is considered the turning point of the Revolution?", "a": "Battle of Saratoga"},
        {"q": "Which battle ended the Revolutionary War?", "a": "Battle of Yorktown"},
        {"q": "Which battle showed Washington's bold surprise attack on Christmas night?", "a": "Battle of Trenton"},
        {"q": "Where did Washington's army suffer through a brutal winter in 1777–78?", "a": "Valley Forge"},

        # ── AMERICAN MILITARY FIGURES ─────────────────────────────────────────
        {"q": "Commander-in-chief of the Continental Army throughout the Revolution", "a": "George Washington"},
        {"q": "Polish engineer who helped train the Continental Army at Valley Forge", "a": "Thaddeus Kosciuszko"},
        {"q": "Prussian officer who drilled and trained the Continental Army at Valley Forge", "a": "Baron von Steuben"},
        {"q": "French officer who became one of Washington's most trusted generals", "a": "Marquis de Lafayette"},
        {"q": "American general who won the Battle of Saratoga", "a": "Horatio Gates"},
        {"q": "American general known for his Southern Campaign victories including Cowpens", "a": "Nathanael Greene"},
        {"q": "American general who later turned traitor and defected to the British", "a": "Benedict Arnold"},
        {"q": "Benedict Arnold's British contact and co-conspirator", "a": "John André"},
        {"q": "'Hero of Saratoga' who was wounded there before his later betrayal", "a": "Benedict Arnold"},
        {"q": "American general nicknamed 'Mad Anthony'", "a": "Anthony Wayne"},
        {"q": "American general who won the Battle of Cowpens", "a": "Daniel Morgan"},
        {"q": "Commander of American forces at Bunker Hill", "a": "William Prescott"},
        {"q": "Patriot who reportedly said 'Don't fire until you see the whites of their eyes'", "a": "William Prescott (or Israel Putnam)"},
        {"q": "First secretary of the treasury; former Continental Army officer and Washington aide", "a": "Alexander Hamilton"},
        {"q": "Paul Revere's famous midnight ride warned colonists of this", "a": "British troops marching on Lexington and Concord"},
        {"q": "Patriot who rode with Paul Revere on the midnight ride", "a": "William Dawes"},

        # ── BRITISH MILITARY FIGURES ──────────────────────────────────────────
        {"q": "British commander-in-chief in North America for much of the war", "a": "William Howe"},
        {"q": "British general who surrendered at Saratoga", "a": "John Burgoyne", "hint": "Nicknamed 'Gentleman Johnny'"},
        {"q": "British general who surrendered at Yorktown", "a": "Lord Cornwallis"},
        {"q": "British king during the American Revolution", "a": "King George III"},
        {"q": "British general who replaced Howe as commander in 1778", "a": "Henry Clinton"},
        {"q": "Feared British cavalry commander in the Southern Campaign", "a": "Banastre Tarleton"},

        # ── POLITICAL FIGURES ─────────────────────────────────────────────────
        {"q": "Patriot who said 'Give me liberty, or give me death!'", "a": "Patrick Henry"},
        {"q": "Second President of the United States; key figure at the Continental Congress", "a": "John Adams"},
        {"q": "Cousin of John Adams; organizer of Boston resistance and Sons of Liberty", "a": "Samuel Adams"},
        {"q": "President of the Continental Congress; largest signature on the Declaration", "a": "John Hancock"},
        {"q": "Oldest and most prominent delegate to the Continental Congress", "a": "Benjamin Franklin"},
        {"q": "Benjamin Franklin negotiated this crucial alliance during the Revolution", "a": "French alliance (Treaty of Alliance with France)"},
        {"q": "Year France formally allied with the American colonies", "a": "1778"},
        {"q": "Virginia delegate who proposed independence at the Second Continental Congress", "a": "Richard Henry Lee"},
        {"q": "Author of the Virginia Declaration of Rights, model for the Bill of Rights", "a": "George Mason"},
        {"q": "First Secretary of State of the United States; key Revolution figure", "a": "Thomas Jefferson"},

        # ── FOREIGN ALLIES ────────────────────────────────────────────────────
        {"q": "European nation that provided the most crucial military and financial support to the Revolution", "a": "France"},
        {"q": "French admiral whose fleet was decisive at the Battle of the Chesapeake", "a": "Admiral de Grasse"},
        {"q": "Spain and this country also allied with America against Britain", "a": "Netherlands"},
        {"q": "Polish cavalry commander who died at the Siege of Savannah fighting for America", "a": "Casimir Pulaski"},

        # ── WOMEN & LESSER-KNOWN FIGURES ─────────────────────────────────────
        {"q": "Woman who reportedly sewed the first American flag", "a": "Betsy Ross"},
        {"q": "Patriot woman who spied for Washington and warned of British plans in Philadelphia", "a": "Lydia Darragh"},
        {"q": "Woman who disguised herself as a man to fight in the Continental Army", "a": "Deborah Sampson"},
        {"q": "Native American group that allied with the British during the Revolution", "a": "Iroquois Confederacy (mostly)"},

        # ── SYMBOLS & CULTURE ────────────────────────────────────────────────
        {"q": "The 'Minutemen' were colonial militiamen who could be ready to fight in this amount of time", "a": "One minute"},
        {"q": "Famous painting by Emanuel Leutze depicting Washington's Christmas crossing", "a": "Washington Crossing the Delaware"},
        {"q": "The Liberty Bell is located in this city", "a": "Philadelphia"},
        {"q": "The first official flag of the United States had this many stars and stripes", "a": "13 (one for each colony)"},
        {"q": "The original 13 colonies declared independence from this country", "a": "Great Britain (England)"},
        {"q": "Site of the 'shot heard round the world'", "a": "Lexington (and Concord)"},
        {"q": "Phrase 'the shot heard round the world' was coined by this poet to describe Lexington/Concord", "a": "Ralph Waldo Emerson"},

        # ── AFTERMATH ────────────────────────────────────────────────────────
        {"q": "The Treaty of Paris was signed in this city", "a": "Paris"},
        {"q": "Under the Treaty of Paris, Britain recognized American territory extending west to this river", "a": "Mississippi River"},
        {"q": "First President under the new Constitution", "a": "George Washington"},
        {"q": "The Articles of Confederation were replaced by this document in 1787", "a": "The Constitution"},
        {"q": "City where the Constitutional Convention was held in 1787", "a": "Philadelphia"},
        {"q": "The Bill of Rights consists of this many amendments", "a": "Ten"},
    ]
}
