'use strict';
/* Translation by English phrase: T('Alert Register') returns the Hindi string when the UI is in Hindi
   and a translation exists, otherwise the English text. So any phrase not listed stays English --
   Hindi covers navigation, headings, table headers, statuses, zones, labels and main actions. */
const RN = { lang: 'en' };
const HI = {
  'RAIL-N.E.D. Control Room': 'RAIL-N.E.D. नियंत्रण कक्ष',
  'Railway Narcotics & Explosives Detection · Prototype · SIH 2026': 'रेलवे नशीले पदार्थ एवं विस्फोटक पहचान · प्रोटोटाइप · SIH 2026',
  'Live simulation': 'लाइव सिमुलेशन', 'Contrast': 'कंट्रास्ट', 'Home': 'होम',
  'Online': 'ऑनलाइन', 'Offline (Demo Mode)': 'ऑफ़लाइन (डेमो मोड)', 'events queued': 'इवेंट कतार में',
  'SAMPLE / DEMO DATA — no live sensors connected. Every event here is scripted, not a real detection. Tiruchirappalli Jn platform numbers follow public sources, but the train board is mostly scripted, not the live timetable.':
    'नमूना / डेमो डेटा — कोई लाइव सेंसर कनेक्ट नहीं है। यहाँ हर घटना तैयार है, वास्तविक पहचान नहीं। तिरुचिरापल्ली जं. के प्लेटफ़ॉर्म नंबर सार्वजनिक स्रोतों पर आधारित हैं, पर ट्रेन सूची अधिकतर तैयार है, वास्तविक समय-सारणी नहीं।',
  'RAIL-N.E.D. is a presumptive field screen, not confirmatory lab analysis. Every positive must be verified by FSL / IMS lab confirmation and NDPS Act 1985 Sec. 50 procedure before any legal action.':
    'RAIL-N.E.D. एक प्रारंभिक फ़ील्ड जांच है, पुष्टिकारक प्रयोगशाला विश्लेषण नहीं। किसी भी कानूनी कार्रवाई से पहले हर पॉज़िटिव का FSL / IMS प्रयोगशाला पुष्टि तथा एनडीपीएस अधिनियम 1985 धारा 50 प्रक्रिया से सत्यापन आवश्यक है।',
  // nav
  'Command Centre': 'कमांड सेंटर', 'Alert Register': 'अलर्ट रजिस्टर', 'Platforms & Trains': 'प्लेटफ़ॉर्म एवं ट्रेनें', 'Platform / Train': 'प्लेटफ़ॉर्म / ट्रेन', 'Platform risk ranking': 'प्लेटफ़ॉर्म जोखिम क्रम', 'Trains at platforms': 'प्लेटफ़ॉर्म पर ट्रेनें', 'Device Fleet': 'डिवाइस बेड़ा',
  'Robot Patrol': 'रोबोट गश्त', 'Evidence & Custody': 'साक्ष्य एवं अभिरक्षा', 'FSL Learning Loop': 'FSL लर्निंग लूप', 'Reports & Analytics': 'रिपोर्ट एवं विश्लेषण', 'Admin & Audit': 'प्रशासन एवं ऑडिट',
  'SAMPLE': 'नमूना', 'Station map': 'स्टेशन मानचित्र', 'Operations': 'संचालन', 'Intelligence': 'इंटेलिजेंस', 'Governance': 'शासन',
  // roles
  'RPF Constable': 'आरपीएफ कांस्टेबल', 'Inspector / Post In-charge': 'निरीक्षक / पोस्ट प्रभारी', 'Control Room Supervisor': 'नियंत्रण कक्ष पर्यवेक्षक', 'FSL Liaison': 'FSL संपर्क अधिकारी', 'Bomb Disposal Squad': 'बम निरोधक दस्ता',
  // kpis
  'Scans (24 h)': 'स्कैन (24 घं.)', 'Alerts': 'अलर्ट', 'Under Review': 'समीक्षाधीन', 'Clean': 'स्वच्छ', 'Review': 'समीक्षा', 'Alert': 'चेतावनी',
  'Open Alerts': 'खुले अलर्ट', 'Devices Online': 'ऑनलाइन डिवाइस', 'Robots Patrolling': 'गश्त पर रोबोट', 'Awaiting FSL': 'FSL की प्रतीक्षा', 'Sync Queue': 'सिंक कतार',
  // headings
  'Alerts, last 24 hours': 'अलर्ट, पिछले 24 घंटे', 'Alert tiers': 'अलर्ट स्तर', 'Station risk ranking': 'स्टेशन जोखिम क्रम', 'Live event feed': 'लाइव इवेंट फ़ीड',
  'Route agreement (two-route rule)': 'मार्ग सहमति (दो-मार्ग नियम)', 'Priority queue': 'प्राथमिकता कतार',
  'Time': 'समय', 'Location': 'स्थान', 'Station': 'स्टेशन', 'Zone': 'क्षेत्र', 'Tier': 'स्तर', 'Predicted Label': 'अनुमानित लेबल', 'Confidence': 'विश्वास', 'Device': 'डिवाइस', 'Routes': 'मार्ग', 'Status': 'स्थिति', 'Officer': 'अधिकारी',
  'Search': 'खोजें', 'All': 'सभी', 'Export CSV': 'CSV निर्यात', 'Print': 'प्रिंट', 'Reset filters': 'फ़िल्टर रीसेट',
  // statuses
  'New': 'नया', 'Acknowledged': 'स्वीकृत', 'Dispatched': 'भेजा गया', 'FSL pending': 'FSL लंबित', 'Lab confirmed': 'लैब पुष्ट', 'False positive': 'फ़र्ज़ी पॉज़िटिव', 'Closed': 'बंद',
  'Acknowledge': 'स्वीकार करें', 'Dispatch team': 'टीम भेजें', 'Send sample to FSL': 'नमूना FSL भेजें', 'Mark lab confirmed': 'लैब पुष्टि दर्ज करें', 'Mark false positive': 'फ़र्ज़ी पॉज़िटिव दर्ज करें', 'Close (clean)': 'बंद करें',
  // detail
  'Event Detail': 'घटना विवरण', 'Close': 'बंद करें', 'Three routes': 'तीन मार्ग', 'SNIFF': 'सूँघना (SNIFF)', 'HEAT': 'ताप (HEAT)', 'SEE': 'देखना (SEE)',
  'routes agree': 'मार्ग सहमत', 'Sensor trace (SNIFF)': 'सेंसर ट्रेस (SNIFF)', 'HEAT ramp: NO2 vs temperature': 'HEAT रैंप: NO2 बनाम तापमान', 'Timeline': 'समयरेखा',
  'Chain verification': 'चेन सत्यापन', 'Chain intact': 'चेन बरकरार', 'Chain broken — tampering suspected': 'चेन टूटी — छेड़छाड़ की आशंका', 'Device signature': 'डिवाइस हस्ताक्षर',
  'Generate seizure memo': 'ज़ब्ती ज्ञापन बनाएं', 'Copy to clipboard': 'क्लिपबोर्ड पर कॉपी करें', 'Copied.': 'कॉपी हुआ।', 'Officer ID': 'अधिकारी आईडी', 'Notes': 'टिप्पणियाँ', 'Add note': 'टिप्पणी जोड़ें', 'Coordinates': 'निर्देशांक',
  'Workflow': 'कार्यप्रवाह', 'Your role cannot perform this action.': 'आपकी भूमिका यह कार्य नहीं कर सकती।',
  // zones
  'Platform 1': 'प्लेटफ़ॉर्म 1', 'Platform 2': 'प्लेटफ़ॉर्म 2', 'Platform 1A': 'प्लेटफ़ॉर्म 1A', 'Platform 7': 'प्लेटफ़ॉर्म 7', 'Platform 3': 'प्लेटफ़ॉर्म 3', 'Platform 4': 'प्लेटफ़ॉर्म 4', 'Platform 5': 'प्लेटफ़ॉर्म 5', 'Platform 6': 'प्लेटफ़ॉर्म 6', 'Foot Overbridge': 'पैदल ऊपरी पुल', 'Parcel Office': 'पार्सल कार्यालय', 'Entry Gate A': 'प्रवेश द्वार A', 'Entry Gate B': 'प्रवेश द्वार B', 'Coach Yard': 'कोच यार्ड',
  // labels
  'Cannabis (terpene profile match)': 'गांजा (टरपीन प्रोफ़ाइल मिलान)', 'Unknown VOC — needs confirmation': 'अज्ञात VOC — पुष्टि आवश्यक',
  'Acetic-acid marker (heroin-processing proxy)': 'एसिटिक-एसिड मार्कर (हेरोइन-प्रसंस्करण संकेतक)', 'No marker detected': 'कोई मार्कर नहीं मिला',
  'Methyl-benzoate marker (cocaine-processing proxy)': 'मिथाइल-बेंज़ोएट मार्कर (कोकीन-प्रसंस्करण संकेतक)',
  'Nitro/nitrate-class residue (stand-in signature)': 'नाइट्रो/नाइट्रेट-श्रेणी अवशेष (स्टैंड-इन संकेत)', 'Object changed vs last clean scan': 'पिछले स्वच्छ स्कैन से वस्तु बदली',
  // fleet / patrol
  'Handheld units': 'हैंडहेल्ड यूनिट', 'Quadruped robots': 'क्वाड्रपेड रोबोट', 'Battery': 'बैटरी', 'Last sync': 'अंतिम सिंक', 'Firmware': 'फ़र्मवेयर', 'Model version': 'मॉडल संस्करण', 'Sensor health': 'सेंसर स्वास्थ्य',
  'Hold': 'रुकें', 'Resume patrol': 'गश्त फिर शुरू करें', 'Return to dock': 'डॉक पर लौटें', 'Emergency stop': 'आपातकालीन रोक', 'Patrolling': 'गश्त पर', 'Holding': 'रुका हुआ', 'Docking': 'डॉक की ओर', 'E-STOP': 'ई-स्टॉप',
  'Patrol route': 'गश्त मार्ग', 'Last clean scan per segment': 'प्रति खंड अंतिम स्वच्छ स्कैन', 'No-go: 25 kV overhead zone': 'प्रतिबंधित: 25 kV ओवरहेड क्षेत्र',
  // evidence/fsl/reports/admin
  'Chain of custody': 'अभिरक्षा श्रृंखला', 'Verify all records': 'सभी रिकॉर्ड सत्यापित करें', 'Records': 'रिकॉर्ड', 'Hash': 'हैश', 'Signature': 'हस्ताक्षर',
  'Lab results received': 'प्राप्त लैब परिणाम', 'Model versions': 'मॉडल संस्करण', 'Signed update rollout': 'हस्ताक्षरित अपडेट रोलआउट',
  'Alerts by hour and zone': 'घंटे और क्षेत्र के अनुसार अलर्ट', 'Substance class mix': 'पदार्थ श्रेणी मिश्रण', 'Median time to acknowledge': 'स्वीकार करने का माध्य समय',
  'Roles & permissions': 'भूमिकाएँ एवं अनुमतियाँ', 'Zone alert thresholds': 'क्षेत्र अलर्ट सीमा', 'Audit log': 'ऑडिट लॉग', 'About this prototype': 'इस प्रोटोटाइप के बारे में', 'Reset demo data': 'डेमो डेटा रीसेट',
};
RN.T = (s) => (RN.lang === 'hi' && HI[s]) || s;
