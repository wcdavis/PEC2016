//
//  pollcalc.java
//
//  Created by Drew Thaler on Sat Oct 09 2004.
//  Updated by Drew Thaler on Fri Sep 12 2008.
//  Updated by Andrew Ferguson on Tue Sep 23 2008.
//      - Updated historical results from 2000 to 2004.
//      - Added option in right-click menu to view state's polling history
//  Updated by Andrew Ferguson on Sat Oct 04 2008.
//  	- Make clicking on pink or light blue states more intuitive
//  Updated by Andrew Ferguson on Sun Jul 08 2012.
//  	- Update for 2012 election.
//  	- Add confidence legend
//  Updated by Andrew Ferguson on Wed Jul 11 2012.
//  	- Change "Confidence" -> "Probability"
//  	- Add white legend for toss-up states
//  	- Change to white text on dark background for "safe state" bar charts
//  Updated by Andrew Ferguson on Wed Sep 26 2012.
//      - Update URLs to point to 2012 data
//      - Include results for 2008, not 2004
//  Updated by Sam Wang on Mon Jun 13 2016.
//      - Include results for 2012, not 2008 (IN, NC)
//  This source code is released into the public domain.
//

import java.awt.*;
import java.awt.event.*;
import java.awt.image.*;
import java.awt.font.*;
import java.awt.geom.*;
import java.applet.*;
import java.io.*;
import javax.imageio.*;
import java.lang.reflect.*;
import java.net.*;
import java.util.*;

class GraphicsShim {
	
	private Graphics g;
	
	public GraphicsShim(Graphics inGraphics) {
		g = inGraphics;
	}
	
	public void enableAntialiasing() {
		Graphics2D  g2d = (Graphics2D)g;
		g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
		g2d.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
	}
	
	public void setStrokeWidth(float width) {
		Graphics2D  g2d = (Graphics2D)g;
		g2d.setStroke(new BasicStroke(width));
	}
}

class StateInfo extends Object
{
	public String   name;
	public String   abbr;
	public int		EV;
	public int[]	positions;
	public double[]	confidence;
	public Polygon  poly;
	public int		labelx;
	public int		labely;
	
	public StateInfo(String inName, String inAbbr, int inEV, int inPos, int[] xcoords, int[] ycoords, int[] inLabelCoords)
	{
		name = inName;
		abbr = inAbbr;
		EV = inEV;
		positions = new int[4];
		confidence = new double[4];
		positions[0] = positions[1] = positions[2] = positions[3] = inPos;
		confidence[0] = confidence[1] = confidence[2] = confidence[3] = 1.0;
		poly = new Polygon(xcoords,ycoords,xcoords.length);
		labelx = inLabelCoords[0];
		labely = inLabelCoords[1];
	}
}

class PollCalculator extends Container
{
	// Parameters
	private Hashtable parameters;
	private String getParameter(String key) { try { return parameters.get(key).toString(); } catch (Exception e) { return null; } }
	
	// We have three different display modes.
	public static final int	DISPLAY_PROJECTION = 0,
								DISPLAY_DECIDED = 1,
								DISPLAY_LAST_ELECTION = 2,
								DISPLAY_CUSTOM = 3;
	
	public int mode = DISPLAY_PROJECTION;
	
	// Candidate names
	final String	demCandidate = "Clinton";
	final String	gopCandidate = "Trump";
	
	// Numbers indicating positions
	public static final int	DEM = 0,
								TOSSUP = 1,
								GOP = 2,
								TOTAL_POSITIONS = 3;
	
	// Colors for each of the positions
	private Color[]   colors = {
		new Color(0x3030FF),
		new Color(0xFFFFFF),
		new Color(0xFF3030)
	};
	
	// Preferred applet width and height
	public static final int HEIGHT = 420,
							 WIDTH = 550;
	
	// Double-buffer for cleaner updates
	private Image   offscreen;
	private boolean updateOffscreenImage;
	
	// Parameters
	public boolean      hasProjection = false;
	public boolean      hasDecided = false;
	public String		bumpMode = "None";
	
	// X,Y coordinates of the 50 states + DC
	final int[] xAL={299,310,310,336,328,299};
	final int[] yAL={300,300,297,297,257,257};
	final int[] xAK={ 68, 76, 92, 89, 71};
	final int[] yAK={320,323,317,299,299};
	final int[] xAZ={114,142,142,117,114};
	final int[] yAZ={232,242,196,191,195};
	final int[] xAR={243,269,272,275,265,235,241};
	final int[] yAR={260,261,254,240,232,232,252};
	final int[] xCA={ 39,114,114, 96, 98, 23,  9, 19};
	final int[] yCA={236,232,195,168,154,132,176,213};
	final int[] xCO={142,163,180,180,180,144}; 
	final int[] yCO={196,198,200,179,165,165};
	final int[] xCT={465,499,491,459}; 
	final int[] yCT={148,127, 99,107};
	final int[] xDE={439,456,458,439,427}; 
	final int[] yDE={219,219,211,192,173};
	final int[] xDC={386,402,417,402}; 
	final int[] yDC={198,213,198,183};
	final int[] xFL={310,335,353,365,372,421,427,394,336,310}; 
	final int[] yFL={300,306,303,306,357,405,363,300,297,297};
	final int[] xGA={336,394,395,360,337,328}; 
	final int[] yGA={297,300,294,257,257,257};
	final int[] xHI={179,199,180,168}; 
	final int[] yHI={352,333,312,320};
	final int[] xID={110,120,135,137,130,128,118,114}; 
	final int[] yID={157,159,162,146,144,130,128,139};
	final int[] xIL={278,288,292,290,285,255,237}; 
	final int[] yIL={237,228,205,149,143,145,174};
	final int[] xIN={288,308,320,309,293,290,292}; 
	final int[] yIN={228,221,206,146,148,149,205};
	final int[] xIA={209,237,255,252,202,202}; 
	final int[] yIA={174,174,145,143,152,157};
	final int[] xKS={180,230,230,211,180}; 
	final int[] yKS={200,202,196,179,179};
	final int[] xKY={278,339,351,345,320,308,288}; 
	final int[] yKY={237,233,218,209,206,221,228};
	final int[] xLA={245,281,292,287,265,271,269,243}; 
	final int[] yLA={297,309,302,287,287,271,261,260};
	final int[] xME={483,495,482,474,471}; 
	final int[] yME={ 65, 40, 19, 20, 33};
	final int[] xMD={375,385,402,417,402,434,456,439,427,372}; 
	final int[] yMD={189,180,183,198,213,233,219,219,173,177};
	final int[] xMA={459,491,515,523,539,483,458,450}; 
	final int[] yMA={107, 99, 98,112,111, 65, 75, 75};
	final int[] xMI={293,309,339,348,344,336,337,309,245,281,309,292,297};
	final int[] yMI={148,146,140,130,115,119,100, 87,100,106, 87,114,135};
	final int[] xMN={202,252,240,245,196,201}; 
	final int[] yMN={152,143,130,100,129,143};
	final int[] xMS={265,287,292,299,299,272,269,271}; 
	final int[] yMS={287,287,302,300,257,254,261,271};
	final int[] xMO={235,265,275,278,237,209,211,230,230}; 
	final int[] yMO={232,232,240,237,174,174,179,196,202};
	final int[] xMT={130,137,161,163,163,128}; 
	final int[] yMT={144,146,147,145,135,130};
	final int[] xNE={161,180,180,211,209,202,161};
	final int[] yNE={165,165,179,179,174,157,157};
	final int[] xNV={114,117,120,110, 98, 96}; 
	final int[] yNV={195,191,159,157,154,168};
	final int[] xNH={458,483,471,462}; 
	final int[] yNH={ 75, 65, 33, 40};
	final int[] xNJ={427,439,458,470,465,427,427,435}; 
	final int[] yNJ={173,192,211,185,148,131,152,163};
	final int[] xNM={142,149,160,163,163,142}; 
	final int[] yNM={242,235,235,202,198,196};
	final int[] xNY={360,415,427,465,459,450,442,410,401,377}; 
	final int[] yNY={127,117,131,148,107, 75, 46, 56, 90, 98};
	final int[] xNC={337,360,387,420,437,434,366}; 
	final int[] yNC={257,257,252,268,253,233,233};
	final int[] xND={163,201,196,163}; 
	final int[] yND={145,143,129,135};
	final int[] xOH={320,345,368,360,339,309}; 
	final int[] yOH={206,209,177,127,140,146};
	final int[] xOK={163,209,209,241,235,230,180,163}; 
	final int[] yOK={202,206,246,252,232,202,200,198};
	final int[] xOR={ 23, 98,110,114, 25}; 
	final int[] yOR={132,154,157,139,127};
	final int[] xPA={368,372,427,435,427,427,415,360}; 
	final int[] yPA={177,177,173,163,152,131,117,127};
	final int[] xRI={499,523,515,491}; 
	final int[] yRI={127,112, 98, 99};
	final int[] xSC={395,420,387,360}; 
	final int[] ySC={294,268,252,257};
	final int[] xSD={161,202,202,201,163,161}; 
	final int[] ySD={157,157,152,143,145,147};
	final int[] xTN={272,299,328,337,366,339,278,275}; 
	final int[] yTN={254,257,257,257,233,233,237,240};
	final int[] xTX={149,182,198,232,236,245,243,241,209,209,163,160}; 
	final int[] yTX={235,276,263,312,302,297,260,252,246,206,202,235};
	final int[] xUT={117,142,144,135,135,120}; 
	final int[] yUT={191,196,165,165,162,159};
	final int[] xVT={450,458,462,442}; 
	final int[] yVT={ 75, 75, 40, 46};
	final int[] xVA={339,366,434,402,386,402,385,369,351}; 
	final int[] yVA={233,233,233,213,198,183,180,210,218};
	final int[] xWA={ 25,114,118, 51, 50, 32, 29}; 
	final int[] yWA={127,139,128,106,112,102,102};
	final int[] xWV={351,369,385,375,372,368,345}; 
	final int[] yWV={218,210,180,189,177,177,209};
	final int[] xWI={252,255,285,287,281,245,240}; 
	final int[] yWI={143,145,143,116,106,100,130};
	final int[] xWY={135,143,161,161,161,137,135}; 
	final int[] yWY={165,165,165,157,147,146,162};
	
	// Label locations of all the states
	final int[][] labels = {
		{ 309, 283 }, {  73, 315 }, { 120, 220 }, { 249, 253 }, {  50, 195 },
		{ 153, 187 }, { 470, 129 }, { 440, 216 }, { 394, 203 }, { 385, 350 },
		{ 346, 285 }, { 178, 334 }, { 117, 152 }, { 263, 185 }, { 298, 190 },
		{ 218, 167 }, { 195, 195 }, { 320, 225 }, { 250, 280 }, { 476,  44 },
		{ 415, 215 }, { 470,  90 }, { 312, 123 }, { 215, 136 }, { 277, 277 },
		{ 237, 213 }, { 139, 143 }, { 186, 174 }, { 102, 173 }, { 461,  62 },
		{ 445, 175 }, { 145, 220 }, { 422, 102 }, { 396, 251 }, { 177, 142 },
		{ 332, 175 }, { 214, 232 }, {  82, 148 }, { 389, 153 }, { 501, 116 },
		{ 386, 276 }, { 178, 155 }, { 308, 252 }, { 179, 242 }, { 123, 185 },
		{ 446,  57 }, { 377, 223 }, {  62, 127 }, { 357, 203 }, { 260, 130 },
		{ 142, 160 }
	};
	
	// State information
    // TODO(adf): the 4th column here is the winner of the state in the previous
    // election. I have commented out the 2004 results (eg, CO was GOP in 2004)
	public StateInfo[] states = {
		new StateInfo("Alabama"				,"AL",  9, GOP, xAL, yAL, labels[ 0]),
		new StateInfo("Alaska"				,"AK",  3, GOP, xAK, yAK, labels[ 1]),
		new StateInfo("Arizona"				,"AZ", 11, GOP, xAZ, yAZ, labels[ 2]),
		new StateInfo("Arkansas"			,"AR",  6, GOP, xAR, yAR, labels[ 3]),
		new StateInfo("California"			,"CA", 55, DEM, xCA, yCA, labels[ 4]),
		new StateInfo("Colorado"			,"CO",  9, DEM /* GOP */, xCO, yCO, labels[ 5]),
		new StateInfo("Connecticut"			,"CT",  7, DEM, xCT, yCT, labels[ 6]),
		new StateInfo("Delaware"			,"DE",  3, DEM, xDE, yDE, labels[ 7]),
		new StateInfo("District of Columbia","DC",  3, DEM, xDC, yDC, labels[ 8]),
		new StateInfo("Florida"				,"FL", 29, DEM /* GOP */, xFL, yFL, labels[ 9]),
		new StateInfo("Georgia"				,"GA", 16, GOP, xGA, yGA, labels[10]),
		new StateInfo("Hawaii"				,"HI",  4, DEM, xHI, yHI, labels[11]),
		new StateInfo("Idaho"				,"ID",  4, GOP, xID, yID, labels[12]),
		new StateInfo("Illinois"			,"IL", 20, DEM, xIL, yIL, labels[13]),
		new StateInfo("Indiana"				,"IN", 11, GOP, xIN, yIN, labels[14]),
		new StateInfo("Iowa"				,"IA",  6, DEM /* GOP */, xIA, yIA, labels[15]),
		new StateInfo("Kansas"				,"KS",  6, GOP, xKS, yKS, labels[16]),
		new StateInfo("Kentucky"			,"KY",  8, GOP, xKY, yKY, labels[17]),
		new StateInfo("Louisiana"			,"LA",  8, GOP, xLA, yLA, labels[18]),
		new StateInfo("Maine"				,"ME",  4, DEM, xME, yME, labels[19]),
		new StateInfo("Maryland"			,"MD", 10, DEM, xMD, yMD, labels[20]),
		new StateInfo("Massachusetts"		,"MA", 11, DEM, xMA, yMA, labels[21]),
		new StateInfo("Michigan"			,"MI", 16, DEM, xMI, yMI, labels[22]),
		new StateInfo("Minnesota"			,"MN", 10, DEM, xMN, yMN, labels[23]),
		new StateInfo("Mississippi"			,"MS",  6, GOP, xMS, yMS, labels[24]),
		new StateInfo("Missouri"			,"MO", 10, GOP, xMO, yMO, labels[25]),
		new StateInfo("Montana"				,"MT",  3, GOP, xMT, yMT, labels[26]),
		new StateInfo("Nebraska"			,"NE",  5, GOP, xNE, yNE, labels[27]),
		new StateInfo("Nevada"				,"NV",  6, DEM /* GOP */, xNV, yNV, labels[28]),
		new StateInfo("New Hampshire"		,"NH",  4, DEM, xNH, yNH, labels[29]),
		new StateInfo("New Jersey"			,"NJ", 14, DEM, xNJ, yNJ, labels[30]),
		new StateInfo("New Mexico"			,"NM",  5, DEM /* GOP */, xNM, yNM, labels[31]),
		new StateInfo("New York"			,"NY", 29, DEM, xNY, yNY, labels[32]),
		new StateInfo("North Carolina"		,"NC", 15, GOP, xNC, yNC, labels[33]),
		new StateInfo("North Dakota"		,"ND",  3, GOP, xND, yND, labels[34]),
		new StateInfo("Ohio"				,"OH", 18, DEM /* GOP */, xOH, yOH, labels[35]),
		new StateInfo("Oklahoma"			,"OK",  7, GOP, xOK, yOK, labels[36]),
		new StateInfo("Oregon"				,"OR",  7, DEM, xOR, yOR, labels[37]),
		new StateInfo("Pennsylvania"		,"PA", 20, DEM, xPA, yPA, labels[38]),
		new StateInfo("Rhode Island"		,"RI",  4, DEM, xRI, yRI, labels[39]),
		new StateInfo("South Carolina"		,"SC",  9, GOP, xSC, ySC, labels[40]),
		new StateInfo("South Dakota"		,"SD",  3, GOP, xSD, ySD, labels[41]),
		new StateInfo("Tennessee"			,"TN", 11, GOP, xTN, yTN, labels[42]),
		new StateInfo("Texas"				,"TX", 38, GOP, xTX, yTX, labels[43]),
		new StateInfo("Utah"				,"UT",  6, GOP, xUT, yUT, labels[44]),
		new StateInfo("Vermont"				,"VT",  3, DEM, xVT, yVT, labels[45]),
		new StateInfo("Virginia"			,"VA", 13, DEM /* GOP */, xVA, yVA, labels[46]),
		new StateInfo("Washington"			,"WA", 12, DEM, xWA, yWA, labels[47]),
		new StateInfo("West Virginia"		,"WV",  5, GOP, xWV, yWV, labels[48]),
		new StateInfo("Wisconsin"			,"WI", 10, DEM, xWI, yWI, labels[49]),
		new StateInfo("Wyoming"				,"WY",  3, GOP, xWY, yWY, labels[50])
	};
	
	// Fonts
    private Font headlineFont = new Font("sans-serif", Font.BOLD, 18);
	private Font subheadFont = new Font("sans-serif", Font.PLAIN, 12);
	private Font labelFont = new Font("sans-serif", Font.PLAIN, 9);
	private Font evFont = new Font("sans-serif", Font.PLAIN, 14);
	private Font evWinnerFont = new Font("sans-serif", Font.BOLD, 14);
	
	// Strings for the interface
	final String headline = "2016 Electoral College Map";
	final String subhead = "The size of each state is distorted to";
	final String subhead2 = "emphasize its share of electoral votes.";
	
	public PollCalculator(Hashtable h)
	{
		parameters = h;
		updateProjection();
		setBackground(new Color(0xFFFFFF));
	}
	
	public void updateProjection()
	{
		String s;
		
		// The current projection is passed as a series of applet parameters.
		for (int i=0; i<states.length; ++i)
		{
			s = getParameter(states[i].abbr + "-projected");
			if (s == null) s = getParameter(states[i].abbr);
			if (s != null) {
				hasProjection = true;
				try {
					int percentDem = Integer.decode(s).intValue();
					
					// Compute the overall position.
					if (percentDem < 40) // used to be 50 (7/16/2012)
						states[i].positions[DISPLAY_PROJECTION] = GOP;
					else if (percentDem > 60) // used to be 50 (7/16/2012)
						states[i].positions[DISPLAY_PROJECTION] = DEM;
					else
						states[i].positions[DISPLAY_PROJECTION] = TOSSUP;
					
					// Copy it into the custom view.
					states[i].positions[DISPLAY_CUSTOM] = states[i].positions[DISPLAY_PROJECTION];
					
					// Compute the confidence in that position as a fraction from 0 to 1
					int delta = Math.abs(50 - percentDem);
					states[i].confidence[DISPLAY_PROJECTION] = (delta / 50.0);
				} catch (Exception e) {
					System.out.println("Invalid value for applet parameter " + states[i].abbr + ": " + s);
				}
			}
		}
		
		// The decided voters may also be passed as a series of applet parameters.
		for (int i=0; i<states.length; ++i)
		{
			s = getParameter(states[i].abbr + "-decided");
			if (s != null) {
				hasDecided = true;
				try {
					int percentDem = Integer.decode(s).intValue();
					
					// Compute the overall position.
					if (percentDem < 50)
						states[i].positions[DISPLAY_DECIDED] = GOP;
					else if (percentDem > 50)
						states[i].positions[DISPLAY_DECIDED] = DEM;
					else
						states[i].positions[DISPLAY_DECIDED] = TOSSUP;
					
					// Compute the confidence in that position as a fraction from 0 to 1
					int delta = Math.abs(50 - percentDem);
					states[i].confidence[DISPLAY_DECIDED] = (delta / 50.0);
				} catch (Exception e) {
					System.out.println("Invalid value for applet parameter " + states[i].abbr + ": " + s);
				}
			}
		}
		
		// Colors may also be passed as applet parameters.
		String colorKeys[] = { "Color.DEM", "Color.TOSSUP", "Color.GOP" };
		for (int i=0; i<colorKeys.length; ++i)
		{
			if ((s = getParameter(colorKeys[i])) != null) {
				try {
					Color   newColor = new Color(Integer.decode(s).intValue());
					colors[i] = newColor;
				} catch (Exception e) {
					System.out.println("Invalid value for applet parameter " + colorKeys[i] + ": " + s);
				}
			}
		}
	}
	
	public Dimension getPreferredSize() {
		return new Dimension(WIDTH,HEIGHT);
	}
	
	public Rectangle getPreferredBounds() {
		return new Rectangle(0, 0, WIDTH, HEIGHT);
	}
	
	public int getPreferredHeight() {
		return HEIGHT;
	}
	
	public int getPreferredWidth() {
		return WIDTH;
	}
	
	public Dimension getMaximumSize() {
		return getPreferredSize();
	}
	
	public Dimension getMinimumSize() {
		return getPreferredSize();
	}
	
	public boolean isDoubleBuffered() {
		return true;
	}
	
	public void repaint() {
		Graphics g;
		if ((g = getGraphics()) != null)
			update(g);
		else
			super.repaint();
	}
	
	public void update(Graphics g) {
		updateOffscreenImage = true;
		paint(g);
	}
	
	public void paint(Graphics g) {
		
		// Create the double-buffer
		if (offscreen == null)
		{
			offscreen = createImage(getPreferredWidth(), getPreferredHeight());
			updateOffscreenImage = true;
		}
		
		// Paint into the double-buffer
		if (updateOffscreenImage)
		{
			Graphics og = offscreen.getGraphics();
			og.setColor(getBackground());
			og.fillRect(0,0,getPreferredWidth(),getPreferredHeight());
			paintOffscreen(og);
			updateOffscreenImage = false;
		}
		
		// Now copy to the display
		g.drawImage(offscreen, 0, 0, this);
	}
	
	public void paintOffscreen (Graphics g) {
		
		int demEV = 0;
		int gopEV = 0;
		int totalEV = 0;
		int position;
		int y;
		
		// Turn on antialiasing.
		try {
			new GraphicsShim(g).enableAntialiasing();
		} catch (Exception e) {}
		
		// Draw the headline.
		g.setColor(Color.black);
		g.setFont(headlineFont);
		y = headlineFont.getSize() + 5;
		g.drawString(headline, 5, y);
		
		// Draw the subhead.
		g.setColor(Color.black);
		g.setFont(subheadFont);
		y += subheadFont.getSize() + 5;
		g.drawString(subhead, 5, y);
		y += subheadFont.getSize() + 5;
		g.drawString(subhead2, 5, y);
		
		// Iterate through the states
		for (int i=0; i<states.length; ++i)
		{
			// Draw this state
			paintState(g,i);
			
			// Compute EV totals
			totalEV += states[i].EV;
			if (states[i].confidence[mode] > 0.9) {
				position = states[i].positions[mode];
				switch (position)
				{
					case GOP:
						gopEV += states[i].EV;
						break;
				
					case DEM:
						demEV += states[i].EV;
						break;
				}
			}
		}
		
		// Draw current EV totals at the bottom.
		paintEVTotals(g,demEV,gopEV,totalEV);

		// Draw a legend in the bottom-right.
		paintLegend(g);
    }
	
	public void paintEVTotals(Graphics g, int demEV, int gopEV, int totalEV)
	{
		int y = 355;
                // get rectangle x offset
		g.setFont((gopEV*2 > totalEV) ? evWinnerFont:evFont);
                int offset = g.getFontMetrics().stringWidth(gopCandidate + " safe: ");
		g.setFont((demEV*2 > totalEV) ? evWinnerFont:evFont);
                offset = Math.max(offset, g.getFontMetrics().stringWidth(demCandidate + " safe: "));

		g.setFont((gopEV*2 > totalEV) ? evWinnerFont:evFont);
		g.setColor(getStateColor(GOP,1.0));
		g.fillRect(2 + offset, y+3, (int) (gopEV * 0.7), g.getFont().getSize() + 3);
		//g.setColor(getBackground());
		//g.fillRect(gopEV+4, y+3, totalEV-gopEV, g.getFont().getSize() + 3);
		g.setColor(Color.black);
		y += g.getFont().getSize() + 3;
		g.drawString(gopCandidate + " safe: ", 5, y);
		g.setColor(Color.white);
		g.drawString(gopEV + " EV", 5 + offset, y);

		g.setFont((demEV*2 > totalEV) ? evWinnerFont:evFont);
		g.setColor(getStateColor(DEM,1.0));
		g.fillRect(2 + offset, y+3, (int) (demEV * 0.7), g.getFont().getSize() + 3);
		//g.setColor(getBackground());
		//g.fillRect(demEV+4, y+3, totalEV-demEV, g.getFont().getSize() + 3);
		g.setColor(Color.black);
		y += g.getFont().getSize() + 4;
		g.drawString(demCandidate + " safe: ", 5, y);
		g.setColor(Color.white);
		g.drawString(demEV + " EV", 5 + offset, y);

		g.setFont(evFont);
		g.setColor(Color.black);
		y += g.getFont().getSize() + 4;
		g.drawString("" + ((totalEV/2)+1) + " EV are required to win.", 5, y);
	}

	public void paintLegend(Graphics g)
	{
		int y = 275;
		int x = 442;

		g.setColor(Color.black);
		g.setFont(evWinnerFont);
		y += evWinnerFont.getSize();
		g.drawString("Probability", x, y);

		g.setFont(subheadFont);

		y += 5;
		g.setColor(getStateColor(DEM, 1.0));
		g.fillRect(x + 2, y, g.getFont().getSize() , g.getFont().getSize());
		g.setColor(Color.black);
		y += g.getFont().getSize();
		g.drawString("> 95% Dem", x + g.getFont().getSize() + 8, y - 2);

		y += 5;
		g.setColor(getStateColor(DEM, 0.60));
		g.fillRect(x + 2, y, g.getFont().getSize() , g.getFont().getSize());
		g.setColor(Color.black);
		y += g.getFont().getSize();
		g.drawString("> 80% Dem", x + g.getFont().getSize() + 8, y - 2);

		y += 5;
		g.setColor(getStateColor(DEM, 0.20));
		g.fillRect(x + 2, y, g.getFont().getSize() , g.getFont().getSize());
		g.setColor(Color.black);
		y += g.getFont().getSize();
		g.drawString("> 60% Dem", x + g.getFont().getSize() + 8, y - 2);

		y += 5;
		g.setColor(getStateColor(TOSSUP, 1.0));
		g.fillRect(x + 2, y, g.getFont().getSize() , g.getFont().getSize());
		g.setColor(Color.black);
		g.drawRect(x + 2, y, g.getFont().getSize() , g.getFont().getSize());
		y += g.getFont().getSize();
		g.drawString("   Toss-up", x + g.getFont().getSize() + 8, y - 2);

		y += 5;
		g.setColor(getStateColor(GOP, 0.20));
		g.fillRect(x + 2, y, g.getFont().getSize() , g.getFont().getSize());
		g.setColor(Color.black);
		y += g.getFont().getSize();
		g.drawString("> 60% Rep", x + g.getFont().getSize() + 8, y - 2);

		y += 5;
		g.setColor(getStateColor(GOP, 0.60));
		g.fillRect(x + 2, y, g.getFont().getSize() , g.getFont().getSize());
		g.setColor(Color.black);
		y += g.getFont().getSize();
		g.drawString("> 80% Rep", x + g.getFont().getSize() + 8, y - 2);

		y += 5;
		g.setColor(getStateColor(GOP, 1.0));
		g.fillRect(x + 2, y, g.getFont().getSize() , g.getFont().getSize());
		g.setColor(Color.black);
		y += g.getFont().getSize();
		g.drawString("> 95% Rep", x + g.getFont().getSize() + 8, y - 2);
	}
	
	public void paintState(Graphics g, int i)
	{
		try {
			// Fill the state with the right color.
			g.setColor(getStateColor(states[i].positions[mode], states[i].confidence[mode]));
			g.fillPolygon(states[i].poly);
			
			// Outline the state.  
			g.setColor(Color.black);
			g.drawPolygon(states[i].poly);
			
			// Draw the label.
			g.setColor(Color.black);
			g.setFont(labelFont);
			g.drawString(states[i].abbr, states[i].labelx, states[i].labely);
		} catch (Exception e) {
			System.out.println(e);
		}
	}
	
	public Color getStateColor(int position, double confidence)
	{
		// Get the base color.  If we're over 90% confident in this
		//  outcome or the state is already a tossup, use the base.
		Color base = colors[position];
		if (confidence > 0.9 || position == TOSSUP)
			return base;
		
		// Otherwise we're going to find a color between the base and
		//  the tossup color.  Extract both components.
		Color tossup = colors[TOSSUP];
		int		baseRGB = base.getRGB();
		int		tossupRGB = tossup.getRGB();
		int		newRGB = 0;
		
		// Adjust the color toward the tossup color based on the confidence.
		for (int j=0; j<3; ++j)
		{
			int baseComponent = (baseRGB >> (8*j)) & 0xFF;
			int tossupComponent = (tossupRGB >> (8*j)) & 0xFF;
			int newComponent = baseComponent + (int)((tossupComponent - baseComponent)
							  * (float)(0.1 + 0.6*(1.0 - confidence/0.9)));
			newComponent = Math.max(0,Math.min(newComponent,0xFF));
			newRGB |= (newComponent << (8*j));
		}
		return new Color(newRGB);
	}
	
	public void setMode(int newMode)
	{
		if (mode != newMode) {
			mode = newMode;
			repaint();
		}
	}
}

public class pollcalc extends Applet implements ItemListener
{
	// This is what actually does the calculation
	private PollCalculator pc;
	
	// Popup menu to switch between modes.
	private PopupMenu			appletMenu;
	private CheckboxMenuItem[]	menuItems = {
		new CheckboxMenuItem("View polling data", false),
		new CheckboxMenuItem("Current projection", false),
		new CheckboxMenuItem("Decided voters only", false),
		new CheckboxMenuItem("Results from 2012", false),
		new CheckboxMenuItem("Custom view", false),
		new CheckboxMenuItem("With +2% for Clinton", false),
		new CheckboxMenuItem("With +2% for Trump", false),
	};
	
	// Mouse tracking
	private boolean		mouseInside;
	private int			mouseOverState;
	private Component   stateDetail;
	
	// Enumerates the properties we support.
	public String[][] getParameterInfo()
	{
		String[][] pinfo = {
			{ "Color.DEM",      "0x000000-0xFFFFFF", "color used to indicate Dem win" },
			{ "Color.GOP",      "0x000000-0xFFFFFF", "color used to indicate GOP win" },
			{ "Color.TOSSUP",   "0x000000-0xFFFFFF", "color used to indicate tossup" },
			{ "AL-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "AL-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "AL",             "0-100",             "synonym for AL-projected" },
			{ "AK-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "AK-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "AK",             "0-100",             "synonym for AK-projected" },
			{ "AZ-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "AZ-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "AZ",             "0-100",             "synonym for AZ-projected" },
			{ "AR-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "AR-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "AR",             "0-100",             "synonym for AR-projected" },
			{ "CA-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "CA-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "CA",             "0-100",             "synonym for CA-projected" },
			{ "CO-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "CO-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "CO",             "0-100",             "synonym for CO-projected" },
			{ "CT-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "CT-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "CT",             "0-100",             "synonym for CT-projected" },
			{ "DE-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "DE-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "DE",             "0-100",             "synonym for DE-projected" },
			{ "DC-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "DC-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "DC",             "0-100",             "synonym for DC-projected" },
			{ "FL-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "FL-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "FL",             "0-100",             "synonym for FL-projected" },
			{ "GA-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "GA-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "GA",             "0-100",             "synonym for GA-projected" },
			{ "HI-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "HI-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "HI",             "0-100",             "synonym for HI-projected" },
			{ "ID-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "ID-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "ID",             "0-100",             "synonym for ID-projected" },
			{ "IL-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "IL-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "IL",             "0-100",             "synonym for IL-projected" },
			{ "IN-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "IN-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "IN",             "0-100",             "synonym for IN-projected" },
			{ "IA-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "IA-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "IA",             "0-100",             "synonym for IA-projected" },
			{ "KS-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "KS-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "KS",             "0-100",             "synonym for KS-projected" },
			{ "KY-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "KY-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "KY",             "0-100",             "synonym for KY-projected" },
			{ "LA-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "LA-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "LA",             "0-100",             "synonym for LA-projected" },
			{ "ME-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "ME-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "ME",             "0-100",             "synonym for ME-projected" },
			{ "MD-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "MD-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "MD",             "0-100",             "synonym for MD-projected" },
			{ "MA-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "MA-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "MA",             "0-100",             "synonym for MA-projected" },
			{ "MI-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "MI-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "MI",             "0-100",             "synonym for MI-projected" },
			{ "MN-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "MN-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "MN",             "0-100",             "synonym for MN-projected" },
			{ "MS-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "MS-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "MS",             "0-100",             "synonym for MS-projected" },
			{ "MO-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "MO-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "MO",             "0-100",             "synonym for MO-projected" },
			{ "MT-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "MT-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "MT",             "0-100",             "synonym for MT-projected" },
			{ "NE-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "NE-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "NE",             "0-100",             "synonym for NE-projected" },
			{ "NV-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "NV-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "NV",             "0-100",             "synonym for NV-projected" },
			{ "NH-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "NH-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "NH",             "0-100",             "synonym for NH-projected" },
			{ "NJ-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "NJ-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "NJ",             "0-100",             "synonym for NJ-projected" },
			{ "NM-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "NM-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "NM",             "0-100",             "synonym for NM-projected" },
			{ "NY-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "NY-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "NY",             "0-100",             "synonym for NY-projected" },
			{ "NC-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "NC-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "NC",             "0-100",             "synonym for NC-projected" },
			{ "ND-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "ND-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "ND",             "0-100",             "synonym for ND-projected" },
			{ "OH-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "OH-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "OH",             "0-100",             "synonym for OH-projected" },
			{ "OK-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "OK-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "OK",             "0-100",             "synonym for OK-projected" },
			{ "OR-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "OR-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "OR",             "0-100",             "synonym for OR-projected" },
			{ "PA-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "PA-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "PA",             "0-100",             "synonym for PA-projected" },
			{ "RI-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "RI-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "RI",             "0-100",             "synonym for RI-projected" },
			{ "SC-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "SC-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "SC",             "0-100",             "synonym for SC-projected" },
			{ "SD-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "SD-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "SD",             "0-100",             "synonym for SD-projected" },
			{ "TN-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "TN-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "TN",             "0-100",             "synonym for TN-projected" },
			{ "TX-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "TX-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "TX",             "0-100",             "synonym for TX-projected" },
			{ "UT-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "UT-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "UT",             "0-100",             "synonym for UT-projected" },
			{ "VT-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "VT-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "VT",             "0-100",             "synonym for VT-projected" },
			{ "VA-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "VA-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "VA",             "0-100",             "synonym for VA-projected" },
			{ "WA-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "WA-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "WA",             "0-100",             "synonym for WA-projected" },
			{ "WV-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "WV-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "WV",             "0-100",             "synonym for WV-projected" },
			{ "WI-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "WI-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "WI",             "0-100",             "synonym for WI-projected" },
			{ "WY-projected",   "0-100",             "projected chance of Dem win among all voters" },
			{ "WY-decided",     "0-100",             "projected chance of Dem win among decided voters" },
			{ "WY",             "0-100",             "synonym for WY-projected" }
		};
		return pinfo;
	};
	
	// Copies out all of our properties into a hashtable.
	public Hashtable getParameters()
	{
		System.out.println("getParameters");
		Hashtable h = new Hashtable();
		String[][] pinfo = getParameterInfo();
		for (int i=0; i<pinfo.length; ++i) {
			String key = pinfo[i][0];
			String val = getParameter(key);
			if (val != null)
				h.put(key,val);
		}
		return h;
	}
	
    public void init()
	{
		System.out.println("pollcalc init");
		pc = new PollCalculator(getParameters());
		enableEvents(AWTEvent.MOUSE_EVENT_MASK |
					AWTEvent.MOUSE_MOTION_EVENT_MASK |
					AWTEvent.ACTION_EVENT_MASK);

		// Set the bumpMode so we know if this is current data, or +2% for Dem, +2% for GOP
		String s;

		if ((s = getParameter("bumpMode")) != null) {
			if (s.equals("None") || s.equals("DEM") || s.equals("GOP")) {
				pc.bumpMode = s;

				if (pc.bumpMode.equals("DEM")) {
					CheckboxMenuItem tmp = menuItems[1];
					menuItems[1] = menuItems[5];
					menuItems[5] = tmp;
				} else if (pc.bumpMode.equals("GOP")) {
					CheckboxMenuItem tmp = menuItems[1];
					menuItems[1] = menuItems[6];
					menuItems[6] = tmp;
				}

			} else {
				System.out.println("Invalid value for applet parameter bumpMode: " + s);
			}
		}
	
		// Create a popup menu
		appletMenu = new PopupMenu("mode");
		for (int i=0; i<menuItems.length; ++i)
		{
			appletMenu.add(menuItems[i]);
			menuItems[i].addItemListener(this);
		}
		add(appletMenu);
		System.out.println("pollcalc init complete");
	}
	
	public void start()
	{
		System.out.println("pollcalc start");
		add(pc);
		// Update the popup menu and mode according to the parameters we have.
		appletMenu.removeAll();
		appletMenu.add(menuItems[0]);
		if (pc.hasProjection)
			appletMenu.add(menuItems[1]);
		if (pc.hasDecided)
			appletMenu.add(menuItems[2]);
		appletMenu.add(menuItems[3]);
		appletMenu.add(menuItems[4]);
		appletMenu.add(menuItems[5]);
		appletMenu.add(menuItems[6]);

		if (pc.mode == pc.DISPLAY_PROJECTION && !pc.hasProjection)
			pc.mode = pc.DISPLAY_DECIDED;
		if (pc.mode == pc.DISPLAY_DECIDED && !pc.hasDecided)
			pc.mode = pc.DISPLAY_LAST_ELECTION;
	}
	
	public void processMouseEvent(MouseEvent e)
	{
		int		modifiers = e.getModifiers();
		boolean button1 = (modifiers & java.awt.event.InputEvent.BUTTON1_MASK) != 0;
		boolean button2 = (modifiers & java.awt.event.InputEvent.BUTTON2_MASK) != 0;
		boolean button3 = (modifiers & java.awt.event.InputEvent.BUTTON3_MASK) != 0;
		boolean ctrl = e.isControlDown();
		boolean shift = e.isShiftDown();
		
		// Handle showing the popup menu.
		if (e.isPopupTrigger() || (e.getID() == MouseEvent.MOUSE_CLICKED && button1 && (ctrl || shift)))
		{
			// Update the checkboxes in the menu before we bring it up.
			menuItems[0].setState(false);
			for (int i=1; i<menuItems.length; ++i)
				menuItems[i].setState(pc.mode == (i - 1));
			appletMenu.show(this, e.getX(), e.getY());

			// Find out what state we're in so we can build the Pollster.com URL
			Point   p = e.getPoint();
			for (int i=0; i < pc.states.length; ++i) {
				if (pc.states[i].poly.contains(p)) {
					mouseOverState = i;
					break;
				}
			}

			return;
		}
		
		// Handle mouse-over
		switch (e.getID())
		{
			case MouseEvent.MOUSE_ENTERED:
				mouseInside = true;
				repaint();
				break;
			
			case MouseEvent.MOUSE_EXITED:
				mouseInside = false;
				repaint();
				break;
		}
		
		// Handle individual clicks.
		if (e.getID() == MouseEvent.MOUSE_CLICKED &&
			button1 && !button2 && !button3)
		{
			Point   p = e.getPoint();
			
			// Handle clicks on a state.
			for (int i=0; i<pc.states.length; ++i) {
				if (pc.states[i].poly.contains(p)) {
					processStateClick(e,i);
					return;
				}
			}
		}
		
		super.processMouseEvent(e);
	}
	
	public void processStateClick(MouseEvent e, int i)
	{
		int oldMode = pc.mode;

		// If we're not in "custom" view, copy the current map
		//  over to the custom view.
		if (pc.mode != pc.DISPLAY_CUSTOM) {
			for (int j=0; j<pc.states.length; ++j)
				pc.states[j].positions[pc.DISPLAY_CUSTOM] = pc.states[j].positions[pc.mode];
			pc.setMode(pc.DISPLAY_CUSTOM);
		}
		
		// Change the state's position.
		if (oldMode == pc.DISPLAY_CUSTOM) {
			// We're already in custom display, so clicking should always
			// change the state's color 
			if (++pc.states[i].positions[pc.mode] >= pc.TOTAL_POSITIONS)
				pc.states[i].positions[pc.mode] = 0;
		} else {
			// We want clicking on 'pink' states to be come 'red', which
			// happens because of the change to custom display, so we only
			// change the state's color if already has a solid color
			if (pc.states[i].positions[pc.mode] == pc.TOSSUP) {
				++pc.states[i].positions[pc.mode];
			} else if (pc.states[i].confidence[oldMode] > 0.95) {
				if (++pc.states[i].positions[pc.mode] >= pc.TOTAL_POSITIONS)
					pc.states[i].positions[pc.mode] = 0;
			}
		}
		
		// Redraw next chance we get.
		repaint();
	}
	
	public void itemStateChanged( ItemEvent e )
	{
		String label = (String)e.getItem();
		for (int i=0; i<menuItems.length; ++i)
			if (menuItems[i].getLabel().equals(label)) {
				if (label.equals("View polling data")) {
                    String name_lower = pc.states[mouseOverState].name.toLowerCase().replace(' ', '-');
                // TODO(adf): keep, if we want to also have links to 2008 data...
				//	String abbr_lower = pc.states[mouseOverState].abbr.toLowerCase();
				//	String address = "http://www.pollster.com/polls/"+abbr_lower+"/08-"+abbr_lower+"-pres-ge-mvo.php";
                    String address = "http://elections.huffingtonpost.com/pollster/2012-"+name_lower+"-president-romney-vs-obama";
    				try {
						AppletContext a = getAppletContext();
						URL url = new URL(address);
						a.showDocument(url, "_blank");
					} catch (MalformedURLException exc) {
						System.out.println(exc.getMessage());
					}
				} else if (i != 1 && label.equals("With +2% for " + pc.demCandidate)) {
    				try {
						AppletContext a = getAppletContext();
						URL url = new URL(getDocumentBase().toString().split("\\?")[0] + "?dem");
						a.showDocument(url);
					} catch (MalformedURLException exc) {
						System.out.println(exc.getMessage());
					}
				} else if (i != 1 && label.equals("With +2% for " + pc.gopCandidate)) {
    				try {
						AppletContext a = getAppletContext();
						URL url = new URL(getDocumentBase().toString().split("\\?")[0] + "?rep");
						a.showDocument(url);
					} catch (MalformedURLException exc) {
						System.out.println(exc.getMessage());
					}
				} else if (i != 1 && label.equals("Current projection")) {
    				try {
						AppletContext a = getAppletContext();
						URL url = new URL(getDocumentBase().toString().split("\\?")[0]);
						a.showDocument(url);
					} catch (MalformedURLException exc) {
						System.out.println(exc.getMessage());
					}
				} else {
					pc.setMode(i - 1);
				}
			}
	}
	
	public void processMouseMotionEvent(MouseEvent e)
	{
		switch (e.getID())
		{
			case MouseEvent.MOUSE_MOVED:
			case MouseEvent.MOUSE_DRAGGED:
				break;
		}
		super.processMouseMotionEvent(e);
	}
	
	public void repaint() {
		pc.repaint();
	}
	
	public static String validImageTypes()
	{
		String[] types = ImageIO.getWriterFormatNames();
		TreeSet unique = new TreeSet(String.CASE_INSENSITIVE_ORDER);
		for (int i=0; i<types.length; ++i)
			unique.add(types[i].toLowerCase());
		return Arrays.toString(unique.toArray());
	}

	public static void usage()
	{
		System.err.println("usage: pollcalc [param=value ...]");
		System.err.println(" Creates an electoral map image using the applet parameters given on the command line.");
		System.err.println("Required parameters:");
		System.err.println("     output           Output filename");
		System.err.println("Optional parameters:");
		System.err.println("     type             Type of image to create (default = png)");
		
		System.err.println("                      Valid image types: " + validImageTypes());
		System.err.println("     Color.DEM        Color to use for states projected as Dem wins (0x3030FF)");
		System.err.println("     Color.GOP        Color to use for states projected as GOP wins (0xFF3030)");
		System.err.println("     Color.TOSSUP     Color to use for states projected as tossups  (0xFFFFFF)");
		System.err.println("     ST               State projection, as % chance of DEM win. e.g. \"OH=52\"");
		System.exit(1);
	}
	
	public static Hashtable parseArguments(String[] args)
	{
		Hashtable params = new Hashtable();
		for (int i=0; i<args.length; i++)
		{
			try {
				StringTokenizer parser = new StringTokenizer(args[i], "=");
				String name = parser.nextToken().toString();
				String value = parser.nextToken("\"").toString();
				value = value.substring(1);
				params.put (name, value);
			} catch (NoSuchElementException e) {}
		}
		return params;
	}
	
	public static void main(String[] args)
	{
		Hashtable params = parseArguments(args);
		
		final PollCalculator pc = new PollCalculator(params);
		
		// Get the output filename. This is the only required parameter.
		String filename = (String)params.get("output");
		if (filename == null)
			usage();
			
		String type = (String)params.get("type");
		if (type == null)
			type = "png";
		
		// Create an image to draw into.
		BufferedImage bi = new BufferedImage(pc.getPreferredWidth(),pc.getPreferredHeight(), BufferedImage.TYPE_INT_RGB);  
		Graphics g = bi.getGraphics();
		g.setColor(new Color(0xFCFCF4));
		g.fillRect(0,0,pc.getPreferredWidth(),pc.getPreferredHeight());
		pc.paintOffscreen(bi.getGraphics());
		try {
			ImageIO.write(bi, type, new FileOutputStream(filename));
		} catch (Exception e) {
			System.err.println("error writing to file: " + e);
			e.printStackTrace();
		}

		// And again, but with a white background
		g.setColor(Color.white);
		g.fillRect(0,0,pc.getPreferredWidth(),pc.getPreferredHeight());
		pc.paintOffscreen(bi.getGraphics());
		try {
			ImageIO.write(bi, type, new FileOutputStream(filename + "-white"));
		} catch (Exception e) {
			System.err.println("error writing to file: " + e);
			e.printStackTrace();
		}
	}
}

