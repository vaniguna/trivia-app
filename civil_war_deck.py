"""
civil_war_deck.py — Comprehensive American Civil War drill deck.

Answer matching notes (handled in drill_mode.py):
- "Johnson" / "Johnston" alone should be rejected — Andrew Johnson (president) and
  Albert Sidney Johnston (Confederate general) are both major figures
- All other surnames are unambiguous within this deck
"""

CIVIL_WAR_DECK = {
    "name": "American Civil War",
    "icon": "⚔️",
    "description": "Key battles, generals, political figures, dates, and turning points of the Civil War",
    "cards": [

        # ── OVERVIEW & DATES ─────────────────────────────────────────────────
        {"q": "Years of the American Civil War", "a": "1861–1865"},
        {"q": "Date the Civil War began (Confederate attack on this fort)", "a": "April 12, 1861 — Fort Sumter"},
        {"q": "Date the Civil War effectively ended (Lee's surrender)", "a": "April 9, 1865"},
        {"q": "Where did Lee surrender to Grant to end the Civil War?", "a": "Appomattox Court House"},
        {"q": "The Confederate States of America was formed by states that did this", "a": "Seceded (left the Union)"},
        {"q": "First state to secede from the Union", "a": "South Carolina"},
        {"q": "Number of states that formed the Confederacy", "a": "Eleven"},
        {"q": "President of the United States during the Civil War", "a": "Abraham Lincoln"},
        {"q": "President of the Confederate States of America", "a": "Jefferson Davis"},
        {"q": "Capital of the Confederacy", "a": "Richmond, Virginia"},
        {"q": "Union name for the Civil War armies (e.g. Army of the Potomac) vs Confederate (e.g. Army of...)", "a": "Army of Northern Virginia"},

        # ── CAUSES ───────────────────────────────────────────────────────────
        {"q": "The central underlying cause of the Civil War", "a": "Slavery"},
        {"q": "1820 agreement that maintained balance between slave and free states", "a": "Missouri Compromise"},
        {"q": "1850 law requiring Northern states to return escaped enslaved people", "a": "Fugitive Slave Act"},
        {"q": "1854 law that allowed new territories to vote on slavery, repealing the Missouri Compromise", "a": "Kansas-Nebraska Act"},
        {"q": "Violent conflict over slavery in a territory in the 1850s, nicknamed this", "a": "Bleeding Kansas"},
        {"q": "1857 Supreme Court ruling that enslaved people were not citizens and had no rights", "a": "Dred Scott decision"},
        {"q": "Enslaved man at the center of the 1857 Supreme Court case", "a": "Dred Scott"},
        {"q": "Abolitionist novel published in 1852 that inflamed public opinion on slavery", "a": "Uncle Tom's Cabin"},
        {"q": "Author of 'Uncle Tom's Cabin'", "a": "Harriet Beecher Stowe"},
        {"q": "Abolitionist who led a raid on Harper's Ferry in 1859 to start a slave uprising", "a": "John Brown"},
        {"q": "Lincoln's election in 1860 triggered secession because he was seen as opposing this", "a": "Slavery (its expansion)"},
        {"q": "Famous 1858 Senate debates between Lincoln and this opponent shaped national views on slavery", "a": "Stephen Douglas"},

        # ── KEY DOCUMENTS & SPEECHES ──────────────────────────────────────────
        {"q": "Lincoln's proclamation that freed enslaved people in Confederate states, effective January 1, 1863", "a": "Emancipation Proclamation"},
        {"q": "Date the Emancipation Proclamation took effect", "a": "January 1, 1863"},
        {"q": "Amendment that permanently abolished slavery in the United States", "a": "13th Amendment"},
        {"q": "Year the 13th Amendment was ratified", "a": "1865"},
        {"q": "Lincoln's famous speech at the dedication of a military cemetery in Pennsylvania, 1863", "a": "Gettysburg Address"},
        {"q": "Opening words of the Gettysburg Address", "a": "Four score and seven years ago"},
        {"q": "Lincoln's second inaugural address included this famous phrase about healing the nation", "a": "Malice toward none, charity for all"},
        {"q": "Confederate constitution was similar to the US Constitution but explicitly protected this", "a": "Slavery"},

        # ── MAJOR BATTLES: EASTERN THEATER ───────────────────────────────────
        {"q": "First major land battle of the Civil War, July 1861, a Confederate victory near Washington", "a": "First Battle of Bull Run (First Manassas)"},
        {"q": "Confederate name for the battles known to the Union as Bull Run", "a": "Manassas"},
        {"q": "Second major battle at the same Virginia site, August 1862, another Confederate victory", "a": "Second Battle of Bull Run (Second Manassas)"},
        {"q": "Bloodiest single day in American military history, September 1862, in Maryland", "a": "Battle of Antietam (Sharpsburg)"},
        {"q": "Approximate casualties at Antietam in one day", "a": "23,000 (killed, wounded, missing)"},
        {"q": "Union general commanding at Antietam whose caution let Lee escape", "a": "George McClellan"},
        {"q": "Union general who replaced McClellan after Antietam and was crushed at Fredericksburg", "a": "Ambrose Burnside"},
        {"q": "December 1862 battle where Burnside's Union army suffered a disastrous frontal assault", "a": "Battle of Fredericksburg"},
        {"q": "Union general who replaced Burnside and was defeated at Chancellorsville", "a": "Joseph Hooker"},
        {"q": "May 1863 battle considered Lee's greatest victory, despite being outnumbered", "a": "Battle of Chancellorsville"},
        {"q": "Confederate general accidentally shot by his own troops at Chancellorsville", "a": "Stonewall Jackson"},
        {"q": "Turning point battle of the Civil War, July 1–3, 1863, Union victory in Pennsylvania", "a": "Battle of Gettysburg"},
        {"q": "Massive Confederate charge on the third day at Gettysburg", "a": "Pickett's Charge"},
        {"q": "Confederate general who led Pickett's Charge", "a": "George Pickett"},
        {"q": "Union general who commanded at Gettysburg", "a": "George Meade"},
        {"q": "Lee's senior corps commander at Gettysburg, criticized for not attacking sooner", "a": "James Longstreet"},
        {"q": "1864 Union campaign in Virginia where Grant relentlessly pursued Lee", "a": "Overland Campaign"},
        {"q": "Brutal May 1864 battle in Virginia fought in dense forest, heavy casualties on both sides", "a": "Battle of the Wilderness"},
        {"q": "Brutal 1864 battle in Virginia known for the 'Bloody Angle'", "a": "Battle of Spotsylvania Court House"},
        {"q": "June 1864 battle where Union forces suffered massive casualties in a failed frontal assault", "a": "Battle of Cold Harbor"},
        {"q": "Long Union siege of this Virginia city preceded Lee's final retreat in 1864–65", "a": "Siege of Petersburg"},
        {"q": "Union general Philip Sheridan devastated this Virginia valley to deny the South its resources", "a": "Shenandoah Valley"},

        # ── MAJOR BATTLES: WESTERN THEATER ───────────────────────────────────
        {"q": "April 1862 battle in Tennessee — one of the bloodiest in the Western Theater", "a": "Battle of Shiloh"},
        {"q": "Confederate general killed at the Battle of Shiloh", "a": "Albert Sidney Johnston"},
        {"q": "Union general who won at Shiloh and went on to overall command", "a": "Ulysses S. Grant"},
        {"q": "Union victory in 1862 that gave control of New Orleans", "a": "Capture of New Orleans"},
        {"q": "Union admiral who captured New Orleans in 1862", "a": "David Farragut"},
        {"q": "Farragut's famous quote at the Battle of Mobile Bay in 1864", "a": "Damn the torpedoes, full speed ahead"},
        {"q": "Union victory the same week as Gettysburg that gave the Union control of the Mississippi", "a": "Fall of Vicksburg"},
        {"q": "Date Vicksburg surrendered to Grant", "a": "July 4, 1863"},
        {"q": "Confederate general who surrendered Vicksburg on July 4, 1863", "a": "John Pemberton"},
        {"q": "September 1863 Confederate victory in Georgia, one of the South's last major wins", "a": "Battle of Chickamauga"},
        {"q": "November 1863 Union victories that broke the Confederate siege of this Tennessee city", "a": "Battles of Chattanooga"},
        {"q": "Union general Sherman's famous march through Georgia in 1864", "a": "March to the Sea"},
        {"q": "City captured and burned during Sherman's March to the Sea", "a": "Atlanta"},
        {"q": "Sherman's march ended at this Georgia coastal city", "a": "Savannah"},

        # ── NAVAL & IRONCLADS ──────────────────────────────────────────────────
        {"q": "1862 naval battle in which the CSS Virginia fought the USS Monitor", "a": "Battle of Hampton Roads"},
        {"q": "This battle was the first between ironclad warships", "a": "Battle of Hampton Roads"},
        {"q": "Confederate name for the ironclad that fought the Monitor (also its original name)", "a": "CSS Virginia (Merrimack)"},
        {"q": "The Monitor's distinctive feature that revolutionized naval warfare", "a": "Rotating gun turret"},
        {"q": "Confederate submarine that became the first to sink an enemy warship", "a": "H.L. Hunley"},
        {"q": "Union naval strategy to blockade Southern ports and strangle the Confederate economy", "a": "Anaconda Plan"},
        {"q": "General who devised the Anaconda Plan", "a": "Winfield Scott"},

        # ── REVERSE: BATTLE → SIGNIFICANCE ───────────────────────────────────
        {"q": "Which Civil War battle was the bloodiest single day in American history?", "a": "Battle of Antietam"},
        {"q": "Which battle is considered the turning point of the Civil War?", "a": "Battle of Gettysburg"},
        {"q": "Which Union victory gave control of the entire Mississippi River?", "a": "Fall of Vicksburg"},
        {"q": "Where did the Civil War begin?", "a": "Fort Sumter"},
        {"q": "Where did Lee surrender to Grant?", "a": "Appomattox Court House"},
        {"q": "Which battle was the first engagement between ironclad warships?", "a": "Battle of Hampton Roads"},
        {"q": "Which battle is called Lee's greatest victory?", "a": "Battle of Chancellorsville"},
        {"q": "Which December 1862 battle was a catastrophic Union defeat under Burnside?", "a": "Battle of Fredericksburg"},

        # ── UNION MILITARY FIGURES ────────────────────────────────────────────
        {"q": "Union general-in-chief who accepted Lee's surrender at Appomattox", "a": "Ulysses S. Grant"},
        {"q": "Union general who captured Atlanta and marched to the sea", "a": "William Tecumseh Sherman"},
        {"q": "First general-in-chief of the Union Army, removed by Lincoln for excessive caution", "a": "George McClellan"},
        {"q": "Union general whose disastrous attack at Fredericksburg led to his removal", "a": "Ambrose Burnside"},
        {"q": "Ambrose Burnside's distinctive facial hair style gave its name to this word", "a": "Sideburns"},
        {"q": "Union admiral famous for 'Damn the torpedoes, full speed ahead'", "a": "David Farragut"},
        {"q": "First Hispanic-American admiral in US history, Civil War hero", "a": "David Farragut"},
        {"q": "Union cavalry general who devastated the Shenandoah Valley", "a": "Philip Sheridan"},
        {"q": "Union general known for his heroic defense of Little Round Top at Gettysburg", "a": "Joshua Chamberlain"},
        {"q": "Black Union regiment that heroically attacked Fort Wagner in 1863", "a": "54th Massachusetts Infantry"},
        {"q": "Colonel who commanded the 54th Massachusetts at Fort Wagner", "a": "Robert Gould Shaw"},
        {"q": "Union general in chief before Grant, known for organizing the army early in the war", "a": "Henry Halleck"},

        # ── CONFEDERATE MILITARY FIGURES ──────────────────────────────────────
        {"q": "Top Confederate general, commander of the Army of Northern Virginia", "a": "Robert E. Lee"},
        {"q": "Robert E. Lee's military rank before the Civil War — he resigned from this to join the Confederacy", "a": "Colonel (US Army)"},
        {"q": "Confederate general known as 'Stonewall'", "a": "Thomas 'Stonewall' Jackson"},
        {"q": "How Stonewall Jackson earned his nickname (at which battle)", "a": "First Battle of Bull Run"},
        {"q": "Confederate general accidentally shot by his own troops at Chancellorsville", "a": "Stonewall Jackson"},
        {"q": "What killed Stonewall Jackson after being wounded at Chancellorsville", "a": "Pneumonia (after amputation of his arm)"},
        {"q": "Confederate cavalry commander known as the 'Gray Ghost'", "a": "John Mosby"},
        {"q": "Flamboyant Confederate cavalry general known for raids and his plumed hat", "a": "J.E.B. Stuart"},
        {"q": "Confederate general killed at Shiloh, whose death was a major blow to the South", "a": "Albert Sidney Johnston"},
        {"q": "Confederate general who replaced Johnston at Shiloh", "a": "P.G.T. Beauregard"},
        {"q": "Confederate general who fired the first shots at Fort Sumter and later led at Bull Run", "a": "P.G.T. Beauregard"},
        {"q": "Confederate general who led the Army of Tennessee and was blamed for losses at Chattanooga", "a": "Braxton Bragg"},
        {"q": "Lee's senior corps commander, nicknamed 'Old War Horse', at Gettysburg and Chickamauga", "a": "James Longstreet"},
        {"q": "Confederate cavalry general who became a notorious early Klan leader after the war", "a": "Nathan Bedford Forrest"},
        {"q": "Nathan Bedford Forrest was famous for his cavalry raids and this controversial 1864 massacre", "a": "Fort Pillow Massacre"},
        {"q": "Confederate general who replaced Joseph Johnston in defense of Atlanta in 1864", "a": "John Bell Hood"},

        # ── POLITICAL FIGURES ─────────────────────────────────────────────────
        {"q": "President who issued the Emancipation Proclamation", "a": "Abraham Lincoln"},
        {"q": "Lincoln's vice president who became president after his assassination", "a": "Andrew Johnson"},
        {"q": "Lincoln was assassinated at this theater in Washington, D.C.", "a": "Ford's Theatre"},
        {"q": "Date of Lincoln's assassination", "a": "April 14, 1865"},
        {"q": "Man who assassinated Abraham Lincoln", "a": "John Wilkes Booth"},
        {"q": "Lincoln's effective Secretary of War for most of the conflict", "a": "Edwin Stanton"},
        {"q": "Lincoln's Secretary of State who survived an assassination attempt the same night as Lincoln", "a": "William Seward"},
        {"q": "Confederate president, former US Senator from Mississippi", "a": "Jefferson Davis"},
        {"q": "Lincoln's Treasury Secretary who later became Chief Justice of the Supreme Court", "a": "Salmon Chase"},
        {"q": "Abolitionist and formerly enslaved man who advised Lincoln and recruited Black soldiers", "a": "Frederick Douglass"},
        {"q": "Escaped enslaved woman who led dozens to freedom via the Underground Railroad", "a": "Harriet Tubman"},
        {"q": "Harriet Tubman also served as a spy and scout for the Union in this state", "a": "South Carolina"},
        {"q": "Northern Democrats who opposed the war and sought a negotiated peace were called this", "a": "Copperheads (Peace Democrats)"},
        {"q": "Lincoln's opponent in the 1864 presidential election", "a": "George McClellan"},
        {"q": "Lincoln won the 1864 election decisively after Union victories in this Southern city", "a": "Atlanta"},

        # ── SLAVERY & ABOLITION ───────────────────────────────────────────────
        {"q": "Network of secret routes and safe houses used to help enslaved people escape north", "a": "Underground Railroad"},
        {"q": "Most famous conductor of the Underground Railroad", "a": "Harriet Tubman"},
        {"q": "The Emancipation Proclamation freed enslaved people only in these states", "a": "Confederate states (states in rebellion)"},
        {"q": "Border states were slave states that did NOT secede — name one", "a": "Kentucky, Missouri, Maryland, or Delaware"},
        {"q": "Black soldiers in the Union Army served in units called this", "a": "United States Colored Troops (USCT)"},
        {"q": "Approximate number of Black soldiers who served in the Union Army", "a": "180,000"},
        {"q": "June 19, 1865 — the date enslaved people in Texas learned of their freedom, now celebrated as this holiday", "a": "Juneteenth"},

        # ── HOME FRONT & SOCIETY ──────────────────────────────────────────────
        {"q": "First military draft in US history was instituted during the Civil War in this year", "a": "1863"},
        {"q": "Wealthy men could avoid the draft by paying this amount or hiring a substitute", "a": "$300"},
        {"q": "1863 riots in New York City protesting the draft", "a": "New York City Draft Riots"},
        {"q": "Clara Barton is famous for her Civil War nursing role and later founding this organization", "a": "American Red Cross"},
        {"q": "Superintendent of Army Nurses during the Civil War", "a": "Dorothea Dix"},
        {"q": "Civil War-era song 'Battle Hymn of the Republic' was written by this woman", "a": "Julia Ward Howe"},
        {"q": "The Confederate anthem, officially 'I Wish I Was in Dixie's Land'", "a": "Dixie"},
        {"q": "Prison camp in Georgia notorious for its horrific conditions and high death toll", "a": "Andersonville"},
        {"q": "Confederate commandant of Andersonville Prison, the only Confederate tried and executed for war crimes", "a": "Henry Wirz"},

        # ── RECONSTRUCTION ────────────────────────────────────────────────────
        {"q": "Period after the Civil War focused on rebuilding the South and integrating freed enslaved people", "a": "Reconstruction"},
        {"q": "Years of Reconstruction", "a": "1865–1877"},
        {"q": "Agency set up after the war to help formerly enslaved people with food, housing, and legal matters", "a": "Freedmen's Bureau"},
        {"q": "14th Amendment granted this to formerly enslaved people", "a": "Citizenship and equal protection under the law"},
        {"q": "15th Amendment granted Black men this right", "a": "The right to vote"},
        {"q": "Reconstruction ended when federal troops were withdrawn from the South after this disputed election", "a": "Election of 1876 (Compromise of 1877)"},
        {"q": "White supremacist organization founded by Confederate veterans after the war", "a": "Ku Klux Klan (KKK)"},
        {"q": "Laws passed in Southern states after Reconstruction to enforce racial segregation", "a": "Jim Crow laws"},
    ]
}
