"""
revolutionary_war_deck.py — Comprehensive American Revolutionary War drill deck.

Answer matching notes (handled in drill_mode.py):
- "Adams" alone is rejected — both John Adams and Samuel Adams are major figures
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
        {"q": "The 13 original colonies declared independence from this country", "a": "Great Britain (England)"},

        # ── CAUSES & LEAD-UP ─────────────────────────────────────────────────
        {"q": "Rallying cry of the Revolution: 'No taxation without...'", "a": "Representation"},
        {"q": "1765 law that taxed legal documents, newspapers, and pamphlets in the colonies", "a": "Stamp Act"},
        {"q": "1767 laws that taxed imported goods like glass, paper, and tea", "a": "Townshend Acts"},
        {"q": "1773 protest in which colonists dumped British tea into Boston Harbor", "a": "Boston Tea Party"},
        {"q": "Laws passed by Britain in 1774 to punish Massachusetts, called this by colonists", "a": "Intolerable Acts (Coercive Acts)"},
        {"q": "March 1770 incident in which British soldiers killed five colonists in Boston", "a": "Boston Massacre"},
        {"q": "Lawyer who defended the British soldiers accused in the Boston Massacre", "a": "John Adams"},
        {"q": "Colonists who supported independence from Britain", "a": "Patriots"},
        {"q": "Colonists who remained loyal to the British Crown", "a": "Loyalists (Tories)"},
        {"q": "Secret colonial organization that organized resistance to British rule", "a": "Sons of Liberty"},
        {"q": "Leader of the Sons of Liberty in Boston", "a": "Samuel Adams"},
        {"q": "German mercenary soldiers hired by Britain to fight in America", "a": "Hessians"},
        {"q": "Black patriot who was one of the first killed at the Boston Massacre", "a": "Crispus Attucks"},

        # ── CONTINENTAL CONGRESSES ────────────────────────────────────────────
        {"q": "First gathering of colonial delegates in Philadelphia in 1774", "a": "First Continental Congress"},
        {"q": "The First Continental Congress was called in response to these laws", "a": "Intolerable Acts"},
        {"q": "Second gathering of colonial delegates that managed the war and declared independence", "a": "Second Continental Congress"},
        {"q": "Year the Second Continental Congress began", "a": "1775"},
        {"q": "Last attempt by the colonists to reconcile with King George, sent in 1775", "a": "Olive Branch Petition"},
        {"q": "King George's response to the Olive Branch Petition", "a": "He rejected it and declared the colonies in rebellion"},
        {"q": "City where both Continental Congresses met", "a": "Philadelphia"},
        {"q": "President of the Continental Congress; largest signature on the Declaration", "a": "John Hancock"},

        # ── KEY DOCUMENTS ────────────────────────────────────────────────────
        {"q": "Document declaring the colonies' independence, adopted July 4, 1776", "a": "Declaration of Independence"},
        {"q": "Primary author of the Declaration of Independence", "a": "Thomas Jefferson"},
        {"q": "Famous 1776 pamphlet by Thomas Paine that urged independence", "a": "Common Sense"},
        {"q": "Author of 'Common Sense'", "a": "Thomas Paine"},
        {"q": "Thomas Paine's series of essays beginning 'These are the times that try men's souls'", "a": "The American Crisis"},
        {"q": "First constitution of the United States, ratified 1781", "a": "Articles of Confederation"},
        {"q": "The Declaration of Independence opens with these famous words", "a": "We hold these truths to be self-evident"},
        {"q": "Virginia delegate who formally proposed independence at the Second Continental Congress", "a": "Richard Henry Lee"},
        {"q": "Author of the Virginia Declaration of Rights, a model for the Bill of Rights", "a": "George Mason"},
        {"q": "Series of essays written to promote ratification of the Constitution", "a": "The Federalist Papers"},
        {"q": "Primary authors of The Federalist Papers", "a": "Alexander Hamilton, James Madison, and John Jay"},
        {"q": "Pen name used by the authors of The Federalist Papers", "a": "Publius"},
        {"q": "Father of the Constitution, who drafted much of it", "a": "James Madison"},

        # ── MAJOR BATTLES ────────────────────────────────────────────────────
        {"q": "First major battle of the Revolution, fought near Boston in June 1775", "a": "Battle of Bunker Hill"},
        {"q": "Battle of Bunker Hill was actually fought mostly on this nearby hill", "a": "Breed's Hill"},
        {"q": "Washington forced the British evacuation of Boston by seizing this elevated position", "a": "Dorchester Heights"},
        {"q": "Month and year of the British evacuation of Boston", "a": "March 1776"},
        {"q": "1776 battle in which Washington was forced to retreat from New York City", "a": "Battle of Long Island (Battle of Brooklyn)"},
        {"q": "Washington's famous crossing of the Delaware River led to victory at this battle", "a": "Battle of Trenton"},
        {"q": "Date of Washington's surprise attack at Trenton", "a": "December 26, 1776"},
        {"q": "The enemy Washington defeated at Trenton were these hired soldiers", "a": "Hessians"},
        {"q": "Battle in New Jersey following Trenton, a second American victory in early 1777", "a": "Battle of Princeton"},
        {"q": "Turning point battle of the Revolution, October 1777, convinced France to ally with America", "a": "Battle of Saratoga"},
        {"q": "Month and year of the Battle of Saratoga", "a": "October 1777"},
        {"q": "British general who surrendered at Saratoga", "a": "John Burgoyne", "hint": "Nicknamed 'Gentleman Johnny'"},
        {"q": "American general credited with the victory at Saratoga", "a": "Horatio Gates"},
        {"q": "'Hero of Saratoga' wounded there before his later betrayal", "a": "Benedict Arnold"},
        {"q": "1777 battle in Pennsylvania where British forces defeated Washington", "a": "Battle of Brandywine"},
        {"q": "1777 battle in Pennsylvania where Washington's surprise attack went wrong in the fog", "a": "Battle of Germantown"},
        {"q": "Washington's army endured a brutal winter here in 1777–1778", "a": "Valley Forge"},
        {"q": "1778 battle in New Jersey where Washington's army fought the British after leaving Valley Forge", "a": "Battle of Monmouth"},
        {"q": "American general court-martialed for retreating at the Battle of Monmouth", "a": "Charles Lee"},
        {"q": "Woman who carried water to soldiers at the Battle of Monmouth, earning a legendary nickname", "a": "Molly Pitcher (Mary Ludwig Hays)"},
        {"q": "Molly Pitcher's real name", "a": "Mary Ludwig Hays (or Mary McCauley)"},
        {"q": "1780 British victory in South Carolina that nearly destroyed the American southern army", "a": "Battle of Camden"},
        {"q": "American general disgraced at Camden, replaced by Nathanael Greene", "a": "Horatio Gates"},
        {"q": "1780 American victory in South Carolina where frontier militia defeated Loyalist forces", "a": "Battle of King's Mountain"},
        {"q": "1781 American victory in South Carolina where Daniel Morgan defeated Tarleton", "a": "Battle of Cowpens"},
        {"q": "American general who won the Battle of Cowpens", "a": "Daniel Morgan"},
        {"q": "American general who fought Cornwallis to exhaustion across the Carolinas", "a": "Nathanael Greene"},
        {"q": "Final major battle of the Revolutionary War, 1781", "a": "Battle of Yorktown"},
        {"q": "Month and year of the British surrender at Yorktown", "a": "October 1781"},
        {"q": "British general who surrendered at Yorktown", "a": "Lord Cornwallis"},
        {"q": "1781 naval battle that cut off Cornwallis's escape route before Yorktown", "a": "Battle of the Chesapeake (Battle of the Capes)"},
        {"q": "French admiral whose fleet blocked the British at the Battle of the Chesapeake", "a": "Admiral de Grasse"},

        # ── REVERSE: BATTLE → SIGNIFICANCE ──────────────────────────────────
        {"q": "Which battle is considered the turning point of the Revolution?", "a": "Battle of Saratoga"},
        {"q": "Which battle ended the Revolutionary War?", "a": "Battle of Yorktown"},
        {"q": "Which battle featured Washington's bold surprise attack on Christmas night?", "a": "Battle of Trenton"},
        {"q": "Where did Washington's army suffer through a brutal winter in 1777–78?", "a": "Valley Forge"},
        {"q": "Which 1780 battle is considered the turning point of the Southern Campaign?", "a": "Battle of King's Mountain"},

        # ── AMERICAN MILITARY FIGURES ─────────────────────────────────────────
        {"q": "Commander-in-chief of the Continental Army throughout the Revolution", "a": "George Washington"},
        {"q": "Prussian officer who drilled and transformed the Continental Army at Valley Forge", "a": "Baron von Steuben"},
        {"q": "French officer who became one of Washington's most trusted generals", "a": "Marquis de Lafayette"},
        {"q": "American general known for his Southern Campaign victories", "a": "Nathanael Greene"},
        {"q": "American general who turned traitor and defected to the British", "a": "Benedict Arnold"},
        {"q": "Benedict Arnold's British contact and co-conspirator, later hanged as a spy", "a": "John André"},
        {"q": "American general nicknamed 'Mad Anthony'", "a": "Anthony Wayne"},
        {"q": "Commander of American forces at Bunker Hill", "a": "William Prescott"},
        {"q": "Patriot who reportedly said 'Don't fire until you see the whites of their eyes'", "a": "William Prescott (or Israel Putnam)"},
        {"q": "First Secretary of the Treasury; former Continental Army officer and Washington aide", "a": "Alexander Hamilton"},
        {"q": "Continental Navy commander famous for 'I have not yet begun to fight'", "a": "John Paul Jones"},
        {"q": "John Paul Jones's famous quote during his battle with the British ship Serapis", "a": "I have not yet begun to fight"},
        {"q": "Ship commanded by John Paul Jones in his famous battle against the Serapis", "a": "Bonhomme Richard"},
        {"q": "Polish engineer who helped fortify American positions during the Revolution", "a": "Thaddeus Kosciuszko"},
        {"q": "Polish cavalry commander who died at the Siege of Savannah fighting for America", "a": "Casimir Pulaski"},

        # ── SPIES & INTELLIGENCE ──────────────────────────────────────────────
        {"q": "American spy network that provided intelligence to Washington in New York", "a": "Culper Ring (Culper Spy Ring)"},
        {"q": "Nathan Hale's famous last words before being hanged by the British", "a": "I only regret that I have but one life to lose for my country"},
        {"q": "Nathan Hale was hanged by the British for spying for this side", "a": "The Americans (he was a Patriot spy)"},
        {"q": "Black spy who infiltrated Cornwallis's headquarters and fed intelligence to Washington", "a": "James Armistead Lafayette"},

        # ── BRITISH MILITARY FIGURES ──────────────────────────────────────────
        {"q": "British commander-in-chief in North America for much of the early war", "a": "William Howe"},
        {"q": "British general who surrendered at Saratoga", "a": "John Burgoyne"},
        {"q": "British general who surrendered at Yorktown", "a": "Lord Cornwallis"},
        {"q": "British king during the American Revolution", "a": "King George III"},
        {"q": "British general who replaced Howe as commander in 1778", "a": "Henry Clinton"},
        {"q": "Feared British cavalry commander in the Southern Campaign known for brutality", "a": "Banastre Tarleton"},

        # ── POLITICAL FIGURES ─────────────────────────────────────────────────
        {"q": "Patriot who said 'Give me liberty, or give me death!'", "a": "Patrick Henry"},
        {"q": "Second President of the United States; key figure at the Continental Congress", "a": "John Adams"},
        {"q": "Cousin of John Adams; organizer of Boston resistance and Sons of Liberty", "a": "Samuel Adams"},
        {"q": "Oldest and most prominent delegate to the Continental Congress", "a": "Benjamin Franklin"},
        {"q": "Benjamin Franklin negotiated this crucial alliance during the Revolution", "a": "French alliance (Treaty of Alliance with France)"},
        {"q": "Year France formally allied with the American colonies", "a": "1778"},
        {"q": "First Secretary of State of the United States; author of the Declaration", "a": "Thomas Jefferson"},
        {"q": "Benjamin Franklin served as American ambassador to this country during the war", "a": "France"},
        {"q": "British Prime Minister during much of the Revolution, who resigned after Yorktown", "a": "Lord North"},
        {"q": "Wife of John Adams who urged him to 'remember the ladies' in the new laws", "a": "Abigail Adams"},

        # ── FOREIGN ALLIES ────────────────────────────────────────────────────
        {"q": "European nation that provided the most crucial military and financial support to the Revolution", "a": "France"},
        {"q": "Spain and this country also allied with America against Britain", "a": "Netherlands"},
        {"q": "France's main motivation for allying with America was rivalry with this country", "a": "Britain (Great Britain)"},

        # ── WOMEN & DIVERSE FIGURES ───────────────────────────────────────────
        {"q": "Woman who reportedly sewed the first American flag", "a": "Betsy Ross"},
        {"q": "Woman who disguised herself as a man to fight in the Continental Army", "a": "Deborah Sampson"},
        {"q": "Native American group that most strongly allied with the British during the Revolution", "a": "Iroquois Confederacy (Haudenosaunee)"},

        # ── PAUL REVERE & THE MIDNIGHT RIDE ──────────────────────────────────
        {"q": "Paul Revere's famous midnight ride warned colonists of this", "a": "British troops marching on Lexington and Concord"},
        {"q": "Patriot who rode with Paul Revere on the midnight ride", "a": "William Dawes"},
        {"q": "The signal lanterns in the Old North Church — 'one if by land, two if by...'", "a": "Sea"},
        {"q": "Poet who immortalized Paul Revere's ride in an 1860 poem", "a": "Henry Wadsworth Longfellow"},

        # ── SYMBOLS & CULTURE ────────────────────────────────────────────────
        {"q": "The 'Minutemen' were colonial militiamen who could be ready to fight in this amount of time", "a": "One minute"},
        {"q": "Famous painting by Emanuel Leutze depicting Washington's Christmas crossing", "a": "Washington Crossing the Delaware"},
        {"q": "The Liberty Bell is located in this city", "a": "Philadelphia"},
        {"q": "The first official flag of the United States had this many stars and stripes", "a": "13 (one for each original colony)"},
        {"q": "Site of the 'shot heard round the world'", "a": "Lexington (and Concord)"},
        {"q": "Phrase 'the shot heard round the world' was coined by this poet", "a": "Ralph Waldo Emerson"},

        # ── AFTERMATH & CONSTITUTION ──────────────────────────────────────────
        {"q": "The Treaty of Paris was signed in this city", "a": "Paris"},
        {"q": "Under the Treaty of Paris, Britain recognized American territory extending west to this river", "a": "Mississippi River"},
        {"q": "The Articles of Confederation were replaced by this document in 1787", "a": "The Constitution"},
        {"q": "City where the Constitutional Convention was held in 1787", "a": "Philadelphia"},
        {"q": "Year of the Constitutional Convention", "a": "1787"},
        {"q": "First President under the new Constitution", "a": "George Washington"},
        {"q": "The Bill of Rights consists of this many amendments", "a": "Ten"},
    ]
}
