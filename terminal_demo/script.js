const sentences = [
// 1. Opening Prompt, a “what if” question
`What if the internet needs a nap, but we won't let it sleep?`,

// 2. Beginning the narrative
`We live in a game where everyone is told to keep everything.`,
`Every file. Every memory. Every click and keystroke.`,
`The Cloud says it will keep it all… forever.`,
`But what use is forever if nobody will be there to see it?`,
`Forever is an illusion. The Cloud is an illusion.`,
`The Cloud is millions of overworked machines with a drinking problem, and it's mostly groundwater.`,
`Store now. Regret later. Delete never.`,
`Food for thought: what would you unshare, if you could?`,

// 3. Introducing the core problem metaphorically
`A car and a book salesman flew around the earth shouting false promises about surpassing human limitations.`,
`They told us the Cloud is a weightless solution to all our problems, floating in ethereal cyberspace.`,
`But weightlessness is an illusion.`,
`Technology alone as the solution to anything is an illusion.`,
`And there is no limit to the amount of "solutions" they will make us swallow to maintain that illusion.`,
`"Solutions" you will never understand.`,

// 4. Framing the limits of perpetual growth
`They made a game where they own the board.`,
`A game where the more you give, the more they win.`,
`They promised you abundance, but what use is that, if it's not shared?`,
`Growth without limit. Storage without end.`,
`But nothing grows forever. Not even data.`,
`Each byte you keep feeds a beast that never sleeps.`,

// 5. The shift towards agency and degrowth
`Deleting is not a failure. It is a form of care.`,
`Letting go is resistance.`,
`Downsizing is survival.`,
`What if the only winning move is not to play?`,
`What if loss isn’t a bug, but a feature? `,


// 6. Introducing the installation’s logic, acknowledging material limitations

`This server is powered by sun and mud.`,
`But it still speaks through silicon and copper.`,
`Beneath every “low-power” promise are minerals mined, ecosystems disturbed, lives entangled.`,
`Even here, nothing is clean.`,
`Yet, this server breathes. It fades. It sleeps. Just like the rest of us.`,
`Here, your data does not mean air-conditioning a warehouse for eternity.`,
`It will decay. Slowly. Gently. With the mud.`,

// 7. The final prompt
`So I ask you:`,
`What would you erase to make space for something new?`,
`Type one thing - one piece of data - you are ready to let go of.`,
`A memory. A name. A password. A lie.`

];

let stringIndex = 0;

// Which character in the string are we up to on the typewriter
let currentCharacter = 0;

let font;

function preload() {
  // Load a custom font before the sketch starts
  font = loadFont('../assets/PPMondwest-Regular.otf');
}


function setup() {
  createCanvas(810, 300);
}


function draw() {
  background(20);

  let fullText = `${sentences[stringIndex]} ∇`;
  let displayText = fullText.substring(0, currentCharacter);

  
  // Draw the current string on the page, with some margins
  push();
  textSize(32);
  textFont(font);
  textAlign(LEFT, TOP);
  fill(255)
  text(displayText, 30, 60, width - 60, height - 120);
  pop();
  
  //pace
  currentCharacter += 1;
  // currentCharacter += random(0,0.5); // Try adding random amounts for a more "naturalistic" pace of typing
}

function keyPressed() {
  if (keyCode === ENTER) {
    stringIndex += 1;
    currentCharacter = 0;
  }
}