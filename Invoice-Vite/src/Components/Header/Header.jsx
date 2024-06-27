import {  CCollapse, CContainer,  CNavItem, CNavLink, CNavbar, CNavbarBrand, CNavbarNav, CNavbarToggler } from '@coreui/react'
import { useState } from 'react'
import LoginSignUpModal from '../AuthModal/LoginSignUpModal'
import "../../CSS/Header.css"

const Header = () => {
  const [visible, setVisible] = useState(false)
  return (
    <>
      <CNavbar expand="lg" className="Header">
        <CContainer fluid>
          <CNavbarToggler
            aria-label="Toggle navigation"
            aria-expanded={visible}
            onClick={() => setVisible(!visible)}
          />
          <CNavbarBrand className='Header-Title' href="/">Invoice Extractor</CNavbarBrand>
          <CCollapse className="navbar-collapse" visible={visible}>
            <CNavbarNav className="me-auto mb-2 mb-lg-0">
              <CNavItem>
                <CNavLink className='Nav-Links-Docs' href="/Docs">
                  Docs
                </CNavLink>
              </CNavItem>
              <CNavItem>
                <CNavLink className='Nav-Links-About' href="/AboutUs">About Us</CNavLink>
              </CNavItem>
              <CNavItem>
                <CNavLink className='Nav-Links-Contact' href="/Contact" >
                  Contact Us
                </CNavLink>
              </CNavItem>
            </CNavbarNav>
            <div style={{marginRight:"30px"}}>
            <LoginSignUpModal/>
            </div>
          </CCollapse>
        </CContainer>
      </CNavbar>
    </>
  )
}

export default Header
