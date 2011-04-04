/**
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.apache.solr.handler.dataimport;

import javax.xml.transform.Source;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.stream.StreamResult;
import javax.xml.transform.stream.StreamSource;
import java.io.CharArrayReader;
import java.io.CharArrayWriter;
import java.io.Reader;
import java.util.*;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.logging.Logger;

/**
 * <p>
 * An implementation of EntityProcessor which uses a streaming xpath parser to
 * extract values out of XML documents. It is typically used in conjunction with
 * HttpDataSource or FileDataSource.
 * </p>
 * <p/>
 * <p>
 * Refer to <a
 * href="http://wiki.apache.org/solr/DataImportHandler">http://wiki.apache.org/solr/DataImportHandler</a>
 * for more details.
 * </p>
 * <p/>
 * <b>This API is experimental and may change in the future.</b>
 *
 * @version $Id: XPathEntityProcessor.java 682383 2008-08-04 13:36:55Z shalin $
 * @see XPathRecordReader
 * @since solr 1.3
 */
public class XPathEntityProcessor extends EntityProcessorBase {
  private static final Logger LOG = Logger.getLogger(XPathEntityProcessor.class
          .getName());

  protected List<String> placeHolderVariables;

  protected List<String> commonFields;

  private String pk;

  private XPathRecordReader xpathReader;

  protected DataSource<Reader> dataSource;

  protected javax.xml.transform.Transformer xslTransformer;

  protected boolean useSolrAddXml = false;

  protected boolean streamRows   =  false;
  
  private int batchSz = 1000;

  @SuppressWarnings("unchecked")
  public void init(Context context) {
    super.init(context);
    if (xpathReader == null)
      initXpathReader();
    pk = context.getEntityAttribute("pk");
    dataSource = context.getDataSource();

  }

  private void initXpathReader() {
    useSolrAddXml = Boolean.parseBoolean(context
            .getEntityAttribute(USE_SOLR_ADD_SCHEMA));
    streamRows = Boolean.parseBoolean(context
        .getEntityAttribute(STREAM));
    if(context.getEntityAttribute("batchSize") != null){
      batchSz = Integer.parseInt(context.getEntityAttribute("batchSize"));
    }
    String xslt = context.getEntityAttribute(XSL);
    if (xslt != null) {
      xslt = resolver.replaceTokens(xslt);
      try {
        Source xsltSource = new StreamSource(xslt);
        // create an instance of TransformerFactory
        TransformerFactory transFact = TransformerFactory.newInstance();
        xslTransformer = transFact.newTransformer(xsltSource);
        LOG
                .info("Using xslTransformer: "
                        + xslTransformer.getClass().getName());
      } catch (Exception e) {
        throw new DataImportHandlerException(DataImportHandlerException.SEVERE,
                "Error initializing XSL ", e);
      }
    }

    if (useSolrAddXml) {
      // Support solr add documents
      xpathReader = new XPathRecordReader("/add/doc");
      xpathReader.addField("name", "/add/doc/field/@name", true);
      xpathReader.addField("value", "/add/doc/field", true);
    } else {
      String forEachXpath = context.getEntityAttribute(FOR_EACH);
      if (forEachXpath == null)
        throw new DataImportHandlerException(DataImportHandlerException.SEVERE,
                "Entity : " + context.getEntityAttribute("name")
                        + " must have a 'forEach' attribute");

      try {
        xpathReader = new XPathRecordReader(forEachXpath);
        for (Map<String, String> field : context.getAllEntityFields()) {
          if (field.get(XPATH) == null)
            continue;
          xpathReader.addField(field.get(DataImporter.COLUMN),
                  field.get(XPATH), Boolean.parseBoolean(field
                  .get(DataImporter.MULTI_VALUED)));
        }
      } catch (RuntimeException e) {
        throw new DataImportHandlerException(DataImportHandlerException.SEVERE,
                "Exception while reading xpaths for fields", e);
      }
    }

    List<String> l = TemplateString.getVariables(context
            .getEntityAttribute(URL));
    for (String s : l) {
      if (s.startsWith(entityName + ".")) {
        if (placeHolderVariables == null)
          placeHolderVariables = new ArrayList<String>();
        placeHolderVariables.add(s.substring(entityName.length() + 1));
      }
    }
    for (Map<String, String> fld : context.getAllEntityFields()) {
      if (fld.get(COMMON_FIELD) != null && "true".equals(fld.get(COMMON_FIELD))) {
        if (commonFields == null)
          commonFields = new ArrayList<String>();
        commonFields.add(fld.get(DataImporter.COLUMN));
      }
    }

  }

  public Map<String, Object> nextRow() {
    Map<String, Object> result;

    if (!context.isRootEntity())
      return fetchNextRow();

    while (true) {
      result = fetchNextRow();

      if (result == null)
        return null;

      if (pk == null || result.get(pk) != null)
        return result;
    }
  }

  @SuppressWarnings("unchecked")
  private Map<String, Object> fetchNextRow() {
    Map<String, Object> r = null;
    while (true) {
      if (rowcache != null)
        return getFromRowCache();
      if (rowIterator == null)
        initQuery(resolver.replaceTokens(context.getEntityAttribute(URL)));
      r = getNext();
      if (r == null) {
        Object hasMore = getSessionAttribute(HAS_MORE);
        if ("true".equals(hasMore) || Boolean.TRUE.equals(hasMore)) {
          String url = (String) getSessionAttribute(NEXT_URL);
          if (url == null)
            url = context.getEntityAttribute(URL);
          Map namespace = (Map) getSessionAttribute(entityName);
          if (namespace != null)
            resolver.addNamespace(entityName, namespace);
          clearSession();
          initQuery(resolver.replaceTokens(url));
          r = getNext();
          if (r == null)
            return null;
        } else {
          return null;
        }
      }
      r = applyTransformer(r);
      if (r != null)
        return readUsefulVars(r);
    }
  }

  private void initQuery(String s) {
      Reader data = null;
      try {
        final List<Map<String, Object>> rows = new ArrayList<Map<String, Object>>();
        data = dataSource.getData(s);
        if (xslTransformer != null) {
          try {
            SimpleCharArrayReader caw = new SimpleCharArrayReader();
            xslTransformer.transform(new StreamSource(data),
                new StreamResult(caw));
            data = caw.getReader();
          } catch (TransformerException e) {
            throw new DataImportHandlerException(
                DataImportHandlerException.SEVERE,
                "Exception in applying XSL Transformeation", e);
          }
        }
        if(streamRows ){
          rowIterator = getRowIterator(data);
        } else {
          xpathReader.streamRecords(data, new XPathRecordReader.Handler() {
            @SuppressWarnings("unchecked")
            public void handle(Map<String, Object> record, String xpath) {
              rows.add(readRow(record, xpath));
            }
          });
          rowIterator = rows.iterator();
        }
      } finally {
        if (!streamRows) {
          closeIt(data);
        }

      }
    }

    private void closeIt(Reader data) {
      try {
        data.close();
      } catch (Exception e) { /* Ignore */
      }
    }
  private Map<String, Object> readRow(Map<String, Object> record, String xpath) {
     if (useSolrAddXml) {
       List<String> names = (List<String>) record.get("name");
       List<String> values = (List<String>) record.get("value");
       Map<String, Object> row = new HashMap<String, Object>();
       for (int i = 0; i < names.size(); i++) {
         if (row.containsKey(names.get(i))) {
           Object existing = row.get(names.get(i));
           if (existing instanceof List) {
             List list = (List) existing;
             list.add(values.get(i));
           } else {
             List list = new ArrayList();
             list.add(existing);
             list.add(values.get(i));
             row.put(names.get(i), list);
           }
         } else {
           row.put(names.get(i), values.get(i));
         }
       }
       return row;
     } else {
       record.put(XPATH_FIELD_NAME, xpath);
       return  record;
     }
   }


  private static class SimpleCharArrayReader extends CharArrayWriter {
    public Reader getReader() {
      return new CharArrayReader(super.buf, 0, super.count);
    }

  }

  @SuppressWarnings("unchecked")
  private Map<String, Object> readUsefulVars(Map<String, Object> r) {
    Object val = r.get(HAS_MORE);
    if (val != null)
      setSessionAttribute(HAS_MORE, val);
    val = r.get(NEXT_URL);
    if (val != null)
      setSessionAttribute(NEXT_URL, val);
    if (placeHolderVariables != null) {
      Map namespace = getNameSpace();
      for (String s : placeHolderVariables) {
        val = r.get(s);
        if (val != null)
          namespace.put(s, val);
      }
    }
    if (commonFields != null) {
      for (String s : commonFields) {
        Object commonVal = r.get(s);
        if (commonVal != null) {
          setSessionAttribute(s, commonVal);
          getNameSpace().put(s, commonVal);
        } else {
          commonVal = getSessionAttribute(s);
          if (commonVal != null)
            r.put(s, commonVal);
        }
      }
    }
    return r;

  }
  private Iterator<Map<String ,Object>> getRowIterator(final Reader data){
    final BlockingQueue<Map<String, Object>> blockingQueue = new ArrayBlockingQueue<Map<String, Object>>(batchSz);
    final AtomicBoolean isEnd = new AtomicBoolean(false);
    new Thread() {
      public void run() {
        try {
          xpathReader.streamRecords(data, new XPathRecordReader.Handler() {
            @SuppressWarnings("unchecked")
            public void handle(Map<String, Object> record, String xpath) {
              if(isEnd.get()) return ;
              try {
                blockingQueue.offer(readRow(record, xpath), 10, TimeUnit.SECONDS);
              } catch (Exception e) {
                isEnd.set(true);
              }
            }
          });
        } finally {
          closeIt(data);
          try {
            blockingQueue.offer(Collections.EMPTY_MAP, 10, TimeUnit.SECONDS);
          } catch (Exception e) { }
        }
      }
    }.start();

    return new Iterator<Map<String, Object>>() {
      public boolean hasNext() {
        return !isEnd.get();
      }
      public Map<String, Object> next() {
        try {
          Map<String, Object> row = blockingQueue.poll(10, TimeUnit.SECONDS);
          if (row == null || row == Collections.EMPTY_MAP) {
            isEnd.set(true);
            return null;
          }
          return row;
        } catch (InterruptedException e) {
          isEnd.set(true);
          return null;
        }
      }
      public void remove() {
        /*no op*/
      }
    };

  }

  @SuppressWarnings("unchecked")
  private Map getNameSpace() {
    Map namespace = (Map) getSessionAttribute(entityName);
    if (namespace == null) {
      namespace = new HashMap();
      setSessionAttribute(entityName, namespace);
    }
    return namespace;
  }

  public static final String URL = "url";

  public static final String HAS_MORE = "$hasMore";

  public static final String NEXT_URL = "$nextUrl";

  public static final String XPATH_FIELD_NAME = "$forEach";

  public static final String FOR_EACH = "forEach";

  public static final String XPATH = "xpath";

  public static final String COMMON_FIELD = "commonField";

  public static final String USE_SOLR_ADD_SCHEMA = "useSolrAddSchema";

  public static final String XSL = "xsl";

  public static final String STREAM = "stream";

}
