import os

ui_content = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>NouveauClientDialog</class>
 <widget class="QDialog" name="NouveauClientDialog">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>850</width>
    <height>650</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Nouveau Client - Synthetix Enterprise</string>
  </property>
  <property name="styleSheet">
   <string>
    QDialog {
        background-color: #f7f9fb;
    }
    QLabel {
        font-family: 'Inter', sans-serif;
    }
    QLineEdit, QPlainTextEdit {
        font-family: 'Inter', sans-serif;
    }
   </string>
  </property>

  <layout class="QVBoxLayout" name="mainLayout">
   <property name="spacing"><number>0</number></property>
   <property name="leftMargin"><number>32</number></property>
   <property name="topMargin"><number>32</number></property>
   <property name="rightMargin"><number>32</number></property>
   <property name="bottomMargin"><number>32</number></property>
   
   <item>
    <widget class="QFrame" name="mainFrame">
     <property name="styleSheet">
      <string>
       #mainFrame {
           background-color: #f2f4f6;
           border-radius: 12px;
           border: 1px solid rgba(196, 197, 215, 0.3);
       }
      </string>
     </property>
     <layout class="QVBoxLayout" name="verticalLayout_mainFrame">
      <property name="spacing"><number>0</number></property>
      <property name="margin"><number>0</number></property>
      
      <!-- HEADER -->
      <item>
       <widget class="QFrame" name="headerFrame">
        <property name="minimumSize"><size><width>0</width><height>60</height></size></property>
        <property name="styleSheet">
         <string>
          #headerFrame {
              background-color: #f8fafc;
              border-bottom: 1px solid rgba(196, 197, 215, 0.2);
              border-top-left-radius: 12px;
              border-top-right-radius: 12px;
          }
         </string>
        </property>
        <layout class="QHBoxLayout" name="horizontalLayout_header">
         <property name="leftMargin"><number>24</number></property>
         <property name="rightMargin"><number>24</number></property>
         <item>
          <widget class="QLabel" name="iconUserAdd">
           <property name="text"><string>👤</string></property>
           <property name="styleSheet"><string>color: #0037b0; font-size: 20px;</string></property>
          </widget>
         </item>
         <item>
          <widget class="QLabel" name="lblHeaderTitle">
           <property name="text"><string>Nouveau Client</string></property>
           <property name="styleSheet"><string>font-family: 'Manrope'; font-weight: bold; font-size: 18px; color: #191c1e;</string></property>
          </widget>
         </item>
         <item>
          <spacer name="spacerHeader"><property name="orientation"><enum>Qt::Horizontal</enum></property></spacer>
         </item>
         <item>
          <widget class="QPushButton" name="btnClose">
           <property name="text"><string>✕</string></property>
           <property name="styleSheet">
            <string>
             QPushButton {
                 color: #434655; background-color: transparent; border: none; font-size: 16px; padding: 6px; border-radius: 14px;
             }
             QPushButton:hover { background-color: rgba(67, 70, 85, 0.1); }
            </string>
           </property>
          </widget>
         </item>
        </layout>
       </widget>
      </item>

      <!-- CONTENT AREA -->
      <item>
       <widget class="QWidget" name="contentWidget">
        <property name="styleSheet"><string>background-color: transparent;</string></property>
        <layout class="QVBoxLayout" name="verticalLayout_content">
         <property name="spacing"><number>24</number></property>
         <property name="margin"><number>32</number></property>
         
         <!-- Top Toggle -->
         <item>
          <layout class="QVBoxLayout" name="verticalLayout_toggle">
           <property name="spacing"><number>12</number></property>
           <item>
            <widget class="QLabel" name="lblTypeClient">
             <property name="text"><string>TYPE DE CLIENT</string></property>
             <property name="styleSheet"><string>font-size: 10px; font-weight: bold; color: #434655; letter-spacing: 1px;</string></property>
            </widget>
           </item>
           <item>
            <layout class="QHBoxLayout" name="horizontalLayout_toggle">
             <item>
              <widget class="QFrame" name="frameToggle">
               <property name="styleSheet"><string>#frameToggle { background-color: #eceef0; border-radius: 8px; }</string></property>
               <layout class="QHBoxLayout" name="horizontalLayout_btnToggle">
                <property name="spacing"><number>0</number></property>
                <property name="margin"><number>4</number></property>
                <item>
                 <widget class="QPushButton" name="btnEntreprise">
                  <property name="text"><string>Entreprise</string></property>
                  <property name="checkable"><bool>true</bool></property>
                  <property name="checked"><bool>true</bool></property>
                  <property name="styleSheet">
                   <string>
                    QPushButton { background-color: transparent; color: #434655; border: none; border-radius: 6px; padding: 8px 24px; font-weight: 500; }
                    QPushButton:checked { background-color: #ffffff; color: #0037b0; font-weight: bold; }
                   </string>
                  </property>
                 </widget>
                </item>
                <item>
                 <widget class="QPushButton" name="btnParticulier">
                  <property name="text"><string>Particulier</string></property>
                  <property name="checkable"><bool>true</bool></property>
                  <property name="styleSheet">
                   <string>
                    QPushButton { background-color: transparent; color: #434655; border: none; border-radius: 6px; padding: 8px 24px; font-weight: 500; }
                    QPushButton:checked { background-color: #ffffff; color: #0037b0; font-weight: bold; }
                   </string>
                  </property>
                 </widget>
                </item>
               </layout>
              </widget>
             </item>
             <item>
              <spacer name="spacerToggle"><property name="orientation"><enum>Qt::Horizontal</enum></property></spacer>
             </item>
            </layout>
           </item>
          </layout>
         </item>

         <!-- Main Grid -->
         <item>
          <layout class="QHBoxLayout" name="horizontalLayout_grid" stretch="7,5">
           <property name="spacing"><number>40</number></property>
           
           <!-- Left Col -->
           <item>
            <widget class="QWidget" name="widgetLeft">
             <layout class="QVBoxLayout" name="verticalLayout_left">
              <property name="spacing"><number>24</number></property>
              <property name="margin"><number>0</number></property>
              
              <!-- Nom -->
              <item>
               <layout class="QVBoxLayout" name="vl_nom">
                <property name="spacing"><number>6</number></property>
                <item>
                 <widget class="QLabel" name="lblNom">
                  <property name="text"><string>Nom / Raison Sociale</string></property>
                  <property name="styleSheet"><string>font-size: 12px; font-weight: 600; color: #434655;</string></property>
                 </widget>
                </item>
                <item>
                 <widget class="QLineEdit" name="editNom">
                  <property name="placeholderText"><string>Ex: Synthetix Enterprise SARL</string></property>
                  <property name="styleSheet">
                   <string>
                    QLineEdit { background-color: #ffffff; color: #191c1e; font-size: 14px; font-weight: 500; padding: 8px 0px; border: none; border-bottom: 2px solid transparent; }
                    QLineEdit:focus { border-bottom: 2px solid #0037b0; }
                   </string>
                  </property>
                 </widget>
                </item>
               </layout>
              </item>

              <!-- ICE -->
              <item>
               <layout class="QVBoxLayout" name="vl_ice">
                <property name="spacing"><number>6</number></property>
                <item>
                 <widget class="QLabel" name="lblICE">
                  <property name="text"><string>ICE (Identifiant Commun)</string></property>
                  <property name="styleSheet"><string>font-size: 12px; font-weight: 600; color: #434655;</string></property>
                 </widget>
                </item>
                <item>
                 <widget class="QLineEdit" name="editICE">
                  <property name="placeholderText"><string>001234567890000</string></property>
                  <property name="styleSheet">
                   <string>
                    QLineEdit { background-color: #ffffff; color: #191c1e; font-size: 14px; font-weight: 500; padding: 8px 0px; border: none; border-bottom: 2px solid transparent; }
                    QLineEdit:focus { border-bottom: 2px solid #0037b0; }
                   </string>
                  </property>
                 </widget>
                </item>
               </layout>
              </item>

              <!-- Adresse -->
              <item>
               <layout class="QVBoxLayout" name="vl_adresse">
                <property name="spacing"><number>6</number></property>
                <item>
                 <widget class="QLabel" name="lblAdresse">
                  <property name="text"><string>Adresse Complète</string></property>
                  <property name="styleSheet"><string>font-size: 12px; font-weight: 600; color: #434655;</string></property>
                 </widget>
                </item>
                <item>
                 <widget class="QPlainTextEdit" name="editAdresse">
                  <property name="placeholderText"><string>Rue, Ville, Code Postal...</string></property>
                  <property name="maximumSize"><size><width>16777215</width><height>80</height></size></property>
                  <property name="styleSheet">
                   <string>
                    QPlainTextEdit { background-color: #ffffff; color: #191c1e; font-size: 14px; font-weight: 500; padding: 8px 0px; border: none; border-bottom: 2px solid transparent; }
                    QPlainTextEdit:focus { border-bottom: 2px solid #0037b0; }
                   </string>
                  </property>
                 </widget>
                </item>
               </layout>
              </item>
              
              <item>
               <spacer name="spacerLeft"><property name="orientation"><enum>Qt::Vertical</enum></property></spacer>
              </item>
             </layout>
            </widget>
           </item>

           <!-- Right Col -->
           <item>
            <widget class="QWidget" name="widgetRight">
             <layout class="QVBoxLayout" name="verticalLayout_right">
              <property name="spacing"><number>32</number></property>
              <property name="margin"><number>0</number></property>

              <!-- Coordonnées -->
              <item>
               <widget class="QFrame" name="frameCoord">
                <property name="styleSheet"><string>#frameCoord { background-color: #ffffff; border-radius: 12px; border: 1px solid rgba(196, 197, 215, 0.4); }</string></property>
                <layout class="QVBoxLayout" name="vl_coord">
                 <property name="spacing"><number>16</number></property>
                 <property name="margin"><number>24</number></property>
                 
                 <item>
                  <layout class="QHBoxLayout" name="hl_coordTitle">
                   <item><widget class="QLabel" name="iconCoord"><property name="text"><string>📇</string></property></widget></item>
                   <item>
                    <widget class="QLabel" name="lblCoordTitle">
                     <property name="text"><string>COORDONNÉES</string></property>
                     <property name="styleSheet"><string>font-size: 11px; font-weight: bold; color: #434655; letter-spacing: 1px;</string></property>
                    </widget>
                   </item>
                   <item><spacer name="spacerCoordTitle"><property name="orientation"><enum>Qt::Horizontal</enum></property></spacer></item>
                  </layout>
                 </item>

                 <!-- Tels and Email -->
                 <item>
                  <layout class="QVBoxLayout" name="vl_coordInputs">
                   <property name="spacing"><number>16</number></property>
                   
                   <item>
                    <layout class="QVBoxLayout" name="vl_telPrinc">
                     <property name="spacing"><number>4</number></property>
                     <item><widget class="QLabel" name="l_telPrinc"><property name="text"><string>TÉLÉPHONE PRINCIPAL</string></property><property name="styleSheet"><string>font-size: 10px; font-weight: bold; color: rgba(67, 70, 85, 0.6);</string></property></widget></item>
                     <item>
                      <widget class="QLineEdit" name="editTelPrincipal">
                       <property name="placeholderText"><string>+212 600 000 000</string></property>
                       <property name="styleSheet"><string>QLineEdit { background-color: transparent; color: #191c1e; font-size: 14px; font-weight: 500; border: none; border-bottom: 1px solid rgba(196, 197, 215, 0.4); padding: 4px 0px; } QLineEdit:focus { border-bottom: 1px solid #0037b0; }</string></property>
                      </widget>
                     </item>
                    </layout>
                   </item>

                   <item>
                    <layout class="QVBoxLayout" name="vl_telFixe">
                     <property name="spacing"><number>4</number></property>
                     <item><widget class="QLabel" name="l_telFixe"><property name="text"><string>TÉLÉPHONE FIXE</string></property><property name="styleSheet"><string>font-size: 10px; font-weight: bold; color: rgba(67, 70, 85, 0.6);</string></property></widget></item>
                     <item>
                      <widget class="QLineEdit" name="editTelFixe">
                       <property name="placeholderText"><string>+212 500 000 000</string></property>
                       <property name="styleSheet"><string>QLineEdit { background-color: transparent; color: #191c1e; font-size: 14px; font-weight: 500; border: none; border-bottom: 1px solid rgba(196, 197, 215, 0.4); padding: 4px 0px; } QLineEdit:focus { border-bottom: 1px solid #0037b0; }</string></property>
                      </widget>
                     </item>
                    </layout>
                   </item>

                   <item>
                    <layout class="QVBoxLayout" name="vl_email">
                     <property name="spacing"><number>4</number></property>
                     <item><widget class="QLabel" name="l_email"><property name="text"><string>EMAIL</string></property><property name="styleSheet"><string>font-size: 10px; font-weight: bold; color: rgba(67, 70, 85, 0.6);</string></property></widget></item>
                     <item>
                      <widget class="QLineEdit" name="editEmail">
                       <property name="placeholderText"><string>contact@entreprise.com</string></property>
                       <property name="styleSheet"><string>QLineEdit { background-color: transparent; color: #191c1e; font-size: 14px; font-weight: 500; border: none; border-bottom: 1px solid rgba(196, 197, 215, 0.4); padding: 4px 0px; } QLineEdit:focus { border-bottom: 1px solid #0037b0; }</string></property>
                      </widget>
                     </item>
                    </layout>
                   </item>

                  </layout>
                 </item>
                </layout>
               </widget>
              </item>

              <!-- Credit -->
              <item>
               <layout class="QVBoxLayout" name="vl_credit">
                <property name="spacing"><number>12</number></property>
                <item>
                 <widget class="QLabel" name="lblCreditTitle">
                  <property name="text"><string>CREDIT PLAFOND</string></property>
                  <property name="styleSheet"><string>font-size: 11px; font-weight: bold; color: #434655; letter-spacing: 1px;</string></property>
                 </widget>
                </item>
                <item>
                 <layout class="QHBoxLayout" name="hl_credit">
                  <property name="spacing"><number>8</number></property>
                  <item><widget class="QLabel" name="lblDH"><property name="text"><string>DH</string></property><property name="styleSheet"><string>font-size: 16px; font-weight: bold; color: #434655;</string></property></widget></item>
                  <item>
                   <widget class="QLineEdit" name="editCreditPlafond">
                    <property name="text"><string>0.00</string></property>
                    <property name="styleSheet"><string>QLineEdit { background-color: transparent; color: #191c1e; font-family: 'Manrope'; font-size: 24px; font-weight: 800; border: none; border-bottom: 2px solid #1d4ed8; padding: 4px 0px; } QLineEdit:focus { border-bottom: 2px solid #0037b0; }</string></property>
                   </widget>
                  </item>
                 </layout>
                </item>
                <item>
                 <widget class="QLabel" name="lblCreditSub">
                  <property name="text"><string>Limite autorisée pour les transactions à crédit.</string></property>
                  <property name="styleSheet"><string>font-size: 10px; font-weight: 500; font-style: italic; color: rgba(67, 70, 85, 0.6);</string></property>
                 </widget>
                </item>
               </layout>
              </item>

              <item>
               <spacer name="spacerRight"><property name="orientation"><enum>Qt::Vertical</enum></property></spacer>
              </item>
             </layout>
            </widget>
           </item>

          </layout>
         </item>
        </layout>
       </widget>
      </item>

      <!-- FOOTER -->
      <item>
       <widget class="QFrame" name="frameFooter">
        <property name="minimumSize"><size><width>0</width><height>80</height></size></property>
        <property name="styleSheet"><string>#frameFooter { background-color: #f8fafc; border-top: 1px solid rgba(196, 197, 215, 0.2); border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; }</string></property>
        <layout class="QHBoxLayout" name="horizontalLayout_footer">
         <property name="leftMargin"><number>32</number></property>
         <property name="rightMargin"><number>32</number></property>
         <item>
          <widget class="QPushButton" name="btnAnnuler">
           <property name="text"><string>Annuler</string></property>
           <property name="styleSheet"><string>QPushButton { color: #57657a; background-color: transparent; font-size: 14px; font-weight: bold; border: none; border-radius: 6px; padding: 10px 24px; } QPushButton:hover { background-color: rgba(87, 101, 122, 0.1); }</string></property>
          </widget>
         </item>
         <item>
          <spacer name="spacerFooter"><property name="orientation"><enum>Qt::Horizontal</enum></property></spacer>
         </item>
         <item>
          <widget class="QPushButton" name="btnEnregistrer">
           <property name="text"><string>💾 Enregistrer</string></property>
           <property name="styleSheet"><string>QPushButton { background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #0037b0, stop:1 #1d4ed8); color: #ffffff; font-size: 14px; font-weight: bold; border: none; border-radius: 6px; padding: 10px 32px; } QPushButton:hover { background-color: #1d4ed8; }</string></property>
          </widget>
         </item>
        </layout>
       </widget>
      </item>

     </layout>
    </widget>
   </item>
  </layout>
 </widget>
 <resources/>
 <connections/>
</ui>
"""

with open("d:/.Code/ERP_lakgit/program/windows/nouveau_client/nouveau_client.ui", "w", encoding="utf-8") as f:
    f.write(ui_content)

print("Generated nouveau_client.ui successfully.")
