# Keskustelusovellus

Sovelluksessa näkyy keskustelualueita, joista jokaisella on tietty aihe. Alueilla on keskusteluketjuja, jotka muodostuvat viesteistä. Jokainen viesti on joko keskusteluketjun aloitusviesti tai vastaus toiseen viestiin. Jokainen käyttäjä on peruskäyttäjä tai ylläpitäjä.

Sovelluksen ominaisuuksia:

* Käyttäjä voi kirjautua sisään ja ulos sekä luoda uuden tunnuksen.
* Käyttäjä näkee sovelluksen etusivulla listan alueista sekä jokaisen alueen ketjujen ja viestien määrän ja viimeksi lähetetyn viestin ajankohdan.
* Käyttäjä voi luoda alueelle uuden ketjun antamalla ketjun otsikon ja aloitusviestin sisällön.
* Käyttäjä voi kirjoittaa ketjuun uuden viestin vastauksena olemassa olevaan viestiin.
* Käyttäjä voi muokata luomansa ketjun otsikkoa sekä lähettämänsä viestin sisältöä. Käyttäjä voi myös poistaa ketjun tai viestin.
* Käyttäjä voi etsiä kaikki viestit, jotka sisältävät annetun sanan.
* Käyttäjä voi antaa ylä- tai alapeukun viestille. Käyttäjä voi myöhemmin muokata valintaansa.
* Käyttäjä voi lajitella keskustelualueen ketjut ja keskusteluketjun viestit lähetysajan tai yläpeukkujen määrän mukaan.
* Ylläpitäjä voi lisätä ja poistaa keskustelualueita.
* Ylläpitäjä voi luoda salaisen alueen ja määrittää, keillä käyttäjillä on pääsy alueelle.

**Ohjeet sovelluksen ajamiseen paikallisesti:**

1. Kloonaa tämä repositorio omalle koneellesi ja siirry sen juurikansioon. Luo kansioon .env-tiedosto ja määritä sen sisältö seuraavanlaiseksi:

        DATABASE_URL=<tietokannan-paikallinen-osoite>
        SECRET_KEY=<salainen-avain>

2. Seuraavaksi aktivoi virtuaaliympäristö ja asenna sovelluksen riippuvuudet komennoilla

        $ python3 -m venv venv
        $ source venv/bin/activate
        $ pip install -r ./requirements.txt

3. Määritä vielä tietokannan skeema ja lue testidata tietokantaan komennoilla

        $ psql -d <tietokannan-nimi> < schema.sql
        $ psql -d <tietokannan-nimi> < testdata.sql

5. Käynnistä sovellus komennolla

        $ flask run

7. Sovellus löytyy nyt osoitteesta <http://localhost:5000>. Siihen on luettu testidatasta ylläpitäjäkäyttäjä `Admin`, jonka salasana on `asdasd`.
